'''
ABOUT
'''
# Author: Matthieu DE MARI
# Email: matthieu.de.mari@gmail.com
# Version: 1.0


'''
IMPORTS
'''
import numpy as np
from itertools import permutations
import matplotlib.pyplot as plt
from tqdm import tqdm


def get_nth_permutation(seq, n):
    
    # Return the n-th permutation of the array of integer contained in seq
    seqc= list(seq[:])
    seqn= [seqc.pop()]
    divider= 2 # divider is meant to be len(seqn)+1, just a bit faster
    while seqc:
        n, new_n= n // divider, n % divider
        seqn.insert(new_n, seqc.pop())
        divider += 1
    return seqn


class CardGame():
    
    def __init__(self, number_of_cards = 8, fixed_seed = 152, print_val = True):
        
        # Check that the number of cards is valid
        valid_numbers_of_cards = [4, 8, 16, 32]
        assert number_of_cards in valid_numbers_of_cards, "The number of cards should be 4, 8, 16 or 32."
        
        # Define number of cards
        self.number_of_cards = number_of_cards
        
        # Define the maximal number of cards to be revealed by prisoner two 
        self.maximal_revealed_number = int(number_of_cards/2)
        
        # Define the maximal number of swaps to be made by prisoner 1
        self.maximal_swap_number = 1
        
        # Define solved boolean
        self.solved = False
        
        # Define solving swap
        self.solving_swap = None
        
        # Define solving swaps list
        self.solving_swap_list = []
        
        # Print displays
        self.print_val = print_val
        
        # Define seed, if any is given
        max_number_mixes = np.math.factorial(number_of_cards)
        if fixed_seed == None:
            self.fixed_seed = np.random.randint(1, max_number_mixes)
        else:
            self.fixed_seed = int(fixed_seed)
        error_seed_str = "The seed should be an integer between 1 and {}".format(max_number_mixes)
        assert self.fixed_seed >= 1 and self.fixed_seed <= max_number_mixes, error_seed_str
            
        # Define cards to be used
        self.define_cards_list()
        
        # Shuffle the cards
        self.shuffle_cards()
        
        # Display cards for prisoner 1
        if self.print_val:
            self.display_cards(board = self.board_state, title_str = 'Initial mixed up configuration (before swap)')
        
        # Look for swap (brute force)
        self.swap_brute_force_search()
        
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
        
        # Try no swap
        #print("Trying swap:", self.solving_swap)
        #self.check_cyclical_permutations()
        
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
                '''
                if self.solved:
                    break
                    '''
                    
        
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
            
    
    def display_final_results(self):
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
        
        # Display results, if prompted
        if self.print_val and len(swap_list_str) > 0:
            print("The possible swaps here are: {}.".format(swap_list_str))

            # Display configuration after swap    
            '''
            if self.print_val:
                title_str = 'The configuration after the optimal swap {}'.format(swap_str)
                self.display_cards(board = self.board_state, title_str = title_str)
                '''
        
            # Otherwise, display that you could not find a swap
        elif self.print_val:
            print("No swap seems to work in this configuration...")
            
        # Print dictionary (for debugging)
        debugging = False
        if self.print_val and debugging:
            print("-----")
            print("Dictionary of attributes")
            print(self.__dict__)
            

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
                