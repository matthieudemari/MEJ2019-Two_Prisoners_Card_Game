'''
ABOUT
'''

# Author: Matthieu DE MARI
# Email: matthieu.de.mari@gmail.com
# Version: 1.0
# Notes: To be document later.

'''
IMPORTS
'''

from copy import deepcopy
from itertools import permutations
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


'''
COMMON FUNCTIONS
'''

def get_nth_permutation(seq, n):
    
    # Return the n-th permutation of the array of integer contained in sequence
    seqc= list(seq[:])
    seqn= [seqc.pop()]
    divider= 2 # divider is meant to be len(seqn)+1, just a bit faster
    while seqc:
        n, new_n= n // divider, n % divider
        seqn.insert(new_n, seqc.pop())
        divider += 1
    return seqn


'''
CARD_GAME CUSTOM CLASS
'''

class CardGame():
    
    def __init__(self, number_of_cards = 8, fixed_seed = 152, try_brute_force = True, investigate_orbits = True, print_val = True):
        
        # Check that the number of cards is valid
        valid_numbers_of_cards = [4, 8, 16, 32]
        assert number_of_cards in valid_numbers_of_cards, "The number of cards should be 4, 8, 16 or 32."
        # Define number of cards
        self.number_of_cards = number_of_cards
        # Define the maximal number of cards to be revealed by prisoner two 
        self.maximal_revealed_number = int(number_of_cards/2)
        # Define the maximal number of swaps to be made by prisoner 1
        self.maximal_swap_number = 1
        # Try brute force?
        self.try_brute_force = try_brute_force
        # Investigate orbits?
        self.investigate_orbits = investigate_orbits
        if self.try_brute_force:
            # Define solved boolean
            self.solved = False
            # Define solving swap
            self.solving_swap = None
            # Define solving swaps list
            self.solving_swap_list = []
        if self.investigate_orbits:
            # List of orbits in original_board_state
            self.list_of_orbits = []
            # List of proposed swaps
            self.proposed_swaps_list = []
        # Print displays
        self.print_val = print_val
        # Define seed, if any is given
        max_number_mixes = np.math.factorial(number_of_cards)
        if fixed_seed == None:
            fac = 9/10
            self.fixed_seed = int(max_number_mixes*fac + np.random.randint(1, 1000))
        else:
            self.fixed_seed = int(fixed_seed)
        error_seed_str = "The seed should be an integer between 1 and {}".format(max_number_mixes)
        assert self.fixed_seed >= 1 and self.fixed_seed <= max_number_mixes, error_seed_str 
        # Define cards to be used
        self.define_cards_list()
        # Shuffle the cards
        self.shuffle_cards()
        # Look for swap (if brute force search is requested)
        if self.try_brute_force:
            self.swap_brute_force_search()
        # Propose swap using orbites investigation
        if self.investigate_orbits:
            self.propose_swaps_orbits()
        # Display final results
        self.display_final_results()
        
        
    def define_cards_list(self):
        
        # Define cards available
        possible_colors = ['Hearts', 'Spades', 'Diamonds', 'Clubs']
        possible_values = ['A', 'K', 'Q', 'J', '10', '9', '8', '7']
        # Define cards colors to be used
        self.colors_number = 2 if self.number_of_cards in [4, 8] else 4
        self.colors_list = possible_colors[:self.colors_number]
        # Define cards values to be used
        self.values_number = int(self.number_of_cards/self.colors_number)
        self.value_list = possible_values[:self.values_number]
        # Define list of cards
        self.decklist = {"C{}".format(int(i+1)): (self.colors_list[i // self.values_number], \
                         self.value_list[i % self.values_number]) for i in range(self.number_of_cards)}
        # Define position dictionary
        self.position_dictionary = {int(i+1): (int((i // self.values_number) + 1), \
                                    int((i % self.values_number) + 1)) for i in range(self.number_of_cards)}
        # Define sorted configuration
        self.sorted_configuration = {int(i+1): self.decklist["C{}".format(int(i+1))] \
                                     for i in range(self.number_of_cards)}
        
        
    def shuffle_cards(self):
        
        # Define random perumation with fixed_seed
        mixed_sequence = get_nth_permutation([int(i+1) for i in range(self.number_of_cards)], self.fixed_seed)
        # Define original board state after mixup
        self.original_board_state = {int(i+1): self.sorted_configuration[mixed_sequence[i]] \
                                     for i in range(self.number_of_cards)}
        # Define board (for later tryouts)
        self.board_state = self.original_board_state.copy()
        # Display
        if self.print_val:
            print("A new game has started!")
            print("-----")
            print("The initial configuration (before swap, seed = {}) is given below.".format(self.fixed_seed))
            self.display_cards(board = self.board_state, title_str = 'Initial mixed up configuration (before swap)')
            print("The sorted configuration (for reference) is given below.")
            self.display_cards(board = self.sorted_configuration, title_str = 'Sorted configuration (for reference)')
            
    
    def display_cards(self, board, title_str = None):
        
        # Initialize figure
        fig, ax = plt.subplots(figsize = (self.colors_number*5, self.values_number))
        # Add text
        for k, v in board.items():
            tup = self.position_dictionary[k]
            i = tup[0]
            j = tup[1]
            txt_str = v
            plt.text(j - 1.25, i - 1, txt_str)
        # Draw gridlines
        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
        ax.set_xticks(np.arange(-0.5, self.values_number, 1))
        ax.set_yticks(np.arange(-0.5, self.colors_number, 1))
        # Add legend
        if title_str != None and type(title_str) == type('title'):
            plt.title(title_str)
        # Show
        plt.show()
        
    
    def swap_brute_force_search(self):
        
        # Display
        if self.print_val:
            print('-----')
            print('Looking for list of possible swaps via brute force.')
        # Otherwise, try all swaps
        self.counter_swaps = 0
        if not self.solved:
            for i in range(1, self.number_of_cards + 1):
                # Check no permutation by swapping the first card with itself, otherwise, skip the permutation
                min_j = (i + 1)*(i > 1) + i*(i == 1)
                for j in range(min_j, self.number_of_cards + 1):
                    # Swap original board with given permutation
                    self.counter_swaps += 1
                    self.swap_board(i, j)
                    # Check if the swap works
                    self.solving_swap = (i, j)
                    #print("Trying swap:", self.solving_swap)
                    self.check_cyclical_permutations()
                    if self.solved:
                        self.solved = False
                        self.solving_swap_list.append(self.solving_swap)
        # Display
        if self.print_val:
            print('Done.')
            
            
    def swap_board(self, i, j):
        
        if i == j:
            # No swap
            self.board_state = self.original_board_state.copy()
        else:
            # Swap cards 
            self.board_state = self.original_board_state.copy()
            self.board_state[i], self.board_state[j] = self.original_board_state[j], self.original_board_state[i]
        
        
    def check_cyclical_permutations(self):
        
        for start_position in self.position_dictionary.keys():
            # Retrieve target card
            target_card = self.decklist["C{}".format(start_position)]
            # Define initial position
            current_position = list(self.sorted_configuration.values()).index(target_card) + 1
            found_card = False
            reached_max_number = False
            counter = 0
            while not found_card and not reached_max_number:
                # Retrieve card at current position
                current_card = self.board_state[current_position]
                # Increase counter
                counter += 1
                # Update found_card
                found_card = current_card == target_card
                # Update reached_max_number
                reached_max_number = not counter < self.maximal_revealed_number
                # If not our card, update current position
                current_position = list(self.sorted_configuration.values()).index(current_card) + 1
            # Check result of cyclical exploration for given start_position
            if not found_card and reached_max_number:
                break
        # Otherwise, it means that the our strategy applied to the configuration after swap
        # works for every possible target card!
        if found_card:
            self.solved = True
            
            
    def propose_swaps_orbits(self):
        
        # Display
        if self.print_val:
            print("-----")
            print('Investigating orbits and proposing swaps.')
        # Find orbits in original_board_state
        self.list_of_orbits = []
        for card in self.sorted_configuration.values():
            if not any([orbit.is_card_in_orbit(card) for orbit in self.list_of_orbits]):
                my_orbit = Orbit(self.original_board_state, self.sorted_configuration, card)
                self.list_of_orbits.append(my_orbit)
        # Find if there is an orbit with length greater than half of the cards
        is_orbit_larger_than_half = [orbit.length_of_orbit() > self.maximal_revealed_number for orbit in self.list_of_orbits]
        self.larger_orbit_exists = any(is_orbit_larger_than_half)
        if self.larger_orbit_exists:
            # If so, swaps are defined in a way to split this orbit in two smaller orbits
            my_orbit = self.list_of_orbits[is_orbit_larger_than_half.index(True)]
            self.proposed_swaps_list = my_orbit.possible_swaps
            # Otherwise, all swaps between elements of a same orbit work
        else:
            self.proposed_swaps_list = []
            for orbit in self.list_of_orbits:
                self.proposed_swaps_list.extend(orbit.possible_swaps)
            # Unique check
            self.proposed_swaps_list = list(np.sort(np.unique(self.proposed_swaps_list))[::-1])
            '''
            TO BE ADDED.
            In practice, additional swaps exist, which fusion two orbits into one of size smaller than self.maximal_revealed_number.
            '''
            
        # Display
        if self.print_val:
            print('Done.')
    
    
    def check_proposed_swaps_match_with_bf(self, swap_list_str):
        
        # Check if all proposed swaps are in the bf swaps
        for swap in self.proposed_swaps_list:
            # Find reversed swap
            split = swap.split(' <-> ')
            card1 = split[0]
            card2 = split[1]
            swap_rev = str(card2) + " <-> " + str(card1)
            if swap in swap_list_str:
                swap_list_str.remove(swap)
            elif swap_rev in swap_list_str:
                swap_list_str.remove(swap_rev)
            else:
                return False, False
        return True, len(swap_list_str) == 0
    
    
    def display_final_results(self):
        
        # Display
        if self.print_val:
            print("-----")
            print("Final results.")
        # It we managed to find a swap that works, display the swap and the board after swap
        card1 = [self.original_board_state[swap[0]] for swap in self.solving_swap_list]
        card2 = [self.original_board_state[swap[1]] for swap in self.solving_swap_list]
        swap_list_str = []
        for i in range(len(self.solving_swap_list)):
            if card1[i] == card2[i]:
                swap_list_str.append('No swap')
            else:
                swap_list_str.append("{} <-> {}".format(card1[i], card2[i]))
        self.solved = len(swap_list_str) > 0
        # Display results for brute force, if prompted
        if self.print_val and self.try_brute_force:
            if len(swap_list_str) > 0:
                print("-")
                print("The possible swaps (obtained via brute force) are:\n{}.".format(swap_list_str))
                # Otherwise, display that you could not find a swap
            else:
                print("-")
                print("No swap seems to work in this configuration, according to brute force...")
        # Display results for orbits investigation, if prompted
        if self.print_val and self.investigate_orbits:
            print("-")
            print("Below are some proposed swaps (obtained via orbit investigation):\n{}.".format(self.proposed_swaps_list))
        # Check if proposed swaps are in the brute force swaps
        if self.print_val and self.investigate_orbits and self.try_brute_force:
            if self.larger_orbit_exists:
                boolean1, boolean2 = self.check_proposed_swaps_match_with_bf(swap_list_str)
                print("-")
                print("The configuration admits an orbit whose length is striclty larger than half of the cards: True.")
                print("The proposed swaps are contained in the ones proposed by brute force: {}.".format(boolean1))
                print("The proposed swaps match exactly with the one computed via brute force: {}.".format(boolean2))
            else:
                print("-")
                boolean = 'No swap' in swap_list_str and 'No swap' in self.proposed_swaps_list
                print("The configuration is already stable and requires no swap: {}.".format(boolean))
        # Print dictionary (for debugging)
        debugging = False
        if self.print_val and debugging:
            print("-----")
            print("Dictionary of attributes")
            print(self.__dict__)
                
    
'''
ORBIT CUSTOM CLASS
'''

class Orbit():

    def __init__(self, board_state, sorted_configuration, initial_card):

        # Board state
        self.board_state = board_state
        # Sorted board (for reference)
        self.sorted_configuration = sorted_configuration
        # Number of cards
        self.number_of_cards = len(self.board_state.keys())
        # List of cards in orbit
        self.list_of_cards_in_orbit = []
        # List of positions for cards in orbits
        self.list_of_positions_in_orbit = []
        # Recreate orbit from card
        self.recreate_orbit_form_card(initial_card)
        # Length of orbit
        self.orbit_length = self.length_of_orbit()
        # Find swaps
        #self.find_swaps()
        # Find swaps
        self.possible_swaps = self.compute_all_swaps_for_orbit()


    def recreate_orbit_form_card(self, initial_card):
        
        # Find initial card in board_state
        current_position = list(self.sorted_configuration.keys())[list(self.sorted_configuration.values()).index(initial_card)]
        current_card = self.board_state[current_position]
        self.list_of_cards_in_orbit.append(current_card)
        self.list_of_positions_in_orbit.append(current_position)
        # Recreate orbit iteratively
        while True:
            # Retrieve next_ card
            current_position = list(self.sorted_configuration.keys())[list(self.sorted_configuration.values()).index(current_card)]
            current_card = self.board_state[current_position]
            # Append to lists
            if not current_card in self.list_of_cards_in_orbit:
                self.list_of_cards_in_orbit.append(current_card)
                self.list_of_positions_in_orbit.append(current_position)
            # Check if orbit is finished
            if current_card == initial_card:
                break
            

    def is_card_in_orbit(self, card):
        return card in self.list_of_cards_in_orbit
    
    
    def is_swap_in_list(self, swap):
        
        # Find reversed swap
        split = swap.split(' <-> ')
        card1 = split[0]
        card2 = split[1]
        swap_rev = str(card2) + " <-> " + str(card1)
        # Check if swap or swap_rev is in list of swap
        boolean = swap in self.possible_swaps or swap_rev in self.possible_swaps
        return boolean
    

    def length_of_orbit(self):
        return len(self.list_of_cards_in_orbit)
    

    '''
    def find_swaps(self):
        
        # If length of the orbit is strictly greater than half the number of the cards, the swaps should split the orbit into
        # two orbits with size smaller than half the number of the cards.
        if self.orbit_length > self.number_of_cards/2:
            # Initialize possible_swaps
            self.possible_swaps = []
            # Check if length of orbit is even
            if self.orbit_length % 2 == 0:
                swap_length = int(self.orbit_length/2)
                for i in range(swap_length):
                    card1 = self.list_of_cards_in_orbit[i]
                    card2 = self.list_of_cards_in_orbit[i + swap_length]
                    swap = str(card1) + " <-> " + str(card2)
                    self.possible_swaps.append(swap)
            else:
                # If odd length, the swap_length changes
                swap_length = int(np.floor(self.orbit_length/2))
                for i in range(swap_length):
                    card1 = self.list_of_cards_in_orbit[i]
                    card2 = self.list_of_cards_in_orbit[i + swap_length % self.orbit_length]
                    swap = str(card1) + " <-> " + str(card2)
                    if not self.is_swap_in_list(swap):
                        self.possible_swaps.append(swap)
                    card1 = self.list_of_cards_in_orbit[i]
                    card2 = self.list_of_cards_in_orbit[i + swap_length + 1 % self.orbit_length]
                    swap = str(card1) + " <-> " + str(card2)
                    if not self.is_swap_in_list(swap):
                        self.possible_swaps.append(swap)
        else:
            self.possible_swaps = ['No swap']
            '''
            
            
    def compute_all_swaps_for_orbit(self):
        
        # Assert size of orbit is smaller than 2*max_size
        max_size = int(len(list(self.board_state.keys()))/2)
        err_str = "Impossible to split the given orbit into two orbits of length smaller than max_size."
        assert self.orbit_length <= 2*max_size, err_str
        # If orbit longer than 1, or lower than max_size, all swaps work
        if self.orbit_length == 1:
            # Return
            return ["No swap"]
        if max_size >= self.orbit_length:
            swap_list = ["No swap"]
            for idx1 in range(self.orbit_length - 1):
                for idx2 in range(idx1 + 1, self.orbit_length):
                    i1 = list(self.list_of_cards_in_orbit)[idx1]
                    i2 = list(self.list_of_cards_in_orbit)[idx2]
                    swap_tuple = (i1, i2)
                    swap_str = str(swap_tuple[0]) + " <-> " + str(swap_tuple[1])
                    swap_list.append(swap_str)
            # Return
            return swap_list
        # Compute swap list (larger orbit)
        swap_list = []
        for idx1 in range(self.orbit_length):
            min_val = idx1 + self.orbit_length - max_size
            max_val = idx1 + max_size + 1
            idx2_list = [i % self.orbit_length for i in range(min_val, max_val)]
            for idx2 in idx2_list:
                i1 = list(self.list_of_cards_in_orbit)[idx1]
                i2 = list(self.list_of_cards_in_orbit)[idx2]
                swap_tuple = (i1, i2)
                swap_str = str(swap_tuple[0]) + " <-> " + str(swap_tuple[1])
                swap_str_rev = str(swap_tuple[1]) + " <-> " + str(swap_tuple[0]) 
                if not swap_str in swap_list and not swap_str_rev in swap_list:
                    swap_list.append(swap_str)
        # Return
        return swap_list
            

'''
BRUTEFORCE_CHECKER CUSTOM CLASS
'''

class BruteForceChecker():
    
    def __init__(self, number_of_cards, print_val = False):
        
        # Check that the number of cards is valid
        valid_numbers_of_cards = [4, 8, 16, 32]
        assert number_of_cards in valid_numbers_of_cards, "The number of cards should be 4, 8, 16 or 32."
        # Define number of cards
        self.number_of_cards = number_of_cards
        # Define maximal number of mixes
        self.max_number_mixes = np.math.factorial(number_of_cards)
        # Define boolean checker
        self.boolean_checker = True
        # Print values?
        self.print_val = print_val
        # Check all combinations
        self.check_all_mixes()
        # Final display
        if self.boolean_checker:
            print("All configurations seem to work: our strategy is valid for {} cards!".format(number_of_cards))
        
        
    def check_all_mixes(self):
        
        for fixed_seed in tqdm(range(1, self.max_number_mixes + 1)):
            # Display (for tracking)
            if self.print_val:
                print("Checking mixed configuration {} / {}".format(fixed_seed, self.max_number_mixes))
            my_game = CardGame(number_of_cards = self.number_of_cards, fixed_seed = fixed_seed, print_val = False)
            self.boolean_checker = my_game.solved
            # If failed, display
            if not self.boolean_checker:
                print("Mixed configuration {} does not admit a swap that works...".format(fixed_seed))
                max_swaps = int(self.number_of_cards*(self.number_of_cards - 1)/2 + 1)
                print("Tried {} swaps out of {} possible ones.".format(my_game.counter_swaps, max_swaps))
                print("Displaying failing configuration below.")
                title_str = 'A counter-example of a failing mix of cards'
                my_game.display_cards(board = my_game.board_state, title_str = title_str)
                print(my_game.solving_swap_list)
                break
            else:
                if self.print_val:
                    print("Works!")
                    
                    