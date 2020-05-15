# importing libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import os

# setting up values for the grid:
# susceptible
S = 0
# affected
A = 1
# recovered
R = 2
# dead
D = 3
# vaccinated
V = 4


# setting up parameters
# infection chance given contact
beta = 0.01
# recovery chance given infection
gamma = 0.01
# chance of death
death = 0.0001
# chance of loss of immunity
mu = 0.005
# chance of vaccination
vacc = 0.001

# increases in state change chance according to
# number of turns spent in a given state
beta_inc = 0.0
gamma_inc = 0.0
death_inc = 0.0
mu_inc = 0.0

# is ring vaccination being investigated?
ring = False

# coordinates of neighbour cells for neigbour_check
coords = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

# initialising dictionary of lists used to plot line graph
states = {0.0: [], 1.0: [], 2.0: [0.0], 3.0: [0.0], 4.0: [0.0]}

# the number of cell on each side of the grid
grid_size = 100

# fixed colours for each state to allow for labelling
cmap = colors.ListedColormap(
    ['yellow', 'lightpink', 'seagreen', 'gray', 'cyan'])

plot_colors = ['yellow', 'lightpink', 'seagreen', 'gray', 'cyan']

# grid same size as display one containing turns spent in current state
history_grid = np.zeros((grid_size, grid_size))


# creating cell class
# each cell is initialised with a number and a random state
class Cell():
    def __init__(self, number):
        self.state = self.random_state()
        self.number = number
        return

    def random_state(self):
        return np.random.choice([S, A, R, D, V], p=[0.96, 0.04, 0, 0, 0])


# calculates chance of infection based on infected neighbours
# if vaccinated that turn, this is overridden
# if ring vaccination being modelled, no chance of random vaccination
def neighbour_check(state_grid, N, i, j):
    new_state = 0
    final_state = 0
    new_beta = beta + history_grid[j, i] * beta_inc
    for (x, y) in coords:
        if not(x == 0 and y == 0):
            if state_grid[(j+y) % N, (i+x) % N] == A and new_state != A:
                new_state = np.random.choice([S, A], p=[1-new_beta, new_beta])
    if ring is False:
        final_state = np.random.choice([V, new_state], p=[vacc, 1-vacc])
    else:
        final_state = new_state
    return final_state


# creates a grid of N*N Cell objects
# each with a sequential number and random state
def cell_creation(N):
    cells = [[Cell(x + y*N) for y in range(N)] for x in range(N)]
    return cells


# creating a grid of states from the initial cell states
def state_grid(N):
    cells = cell_creation(N)
    state_grid = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            state_grid[j, i] = cells[j][i].state
    return state_grid


def update(frameNum, img, state_grid, N):
    new_grid = state_grid.copy()
    global history_grid
    for i in range(N):
        for j in range(N):
            # if affected, chance of recovery, death, or nothing
            # if susceptible, neighbour_check is run
            # if recovered, chance of loss of immunity
            if state_grid[j, i] == A:
                # calculating new chances based on cell history
                new_gamma = gamma + history_grid[j, i] * gamma_inc
                new_death = death + history_grid[j, i] * death_inc
                new_grid[j, i] = np.random.choice(
                    [A, R, D], p=[1-(new_gamma+new_death),
                                  new_gamma, new_death])
                # if ring vaccination being modelled
                # # vaccinate all neighbours
                if ring is True:
                    for (x, y) in coords:
                        if not(x == 0 and y == 0):
                            if state_grid[(j+y) % N, (i+x) % N] == S:
                                new_grid[(j+y) % N, (i+x) % N] = V
            elif state_grid[j, i] == S:
                new_grid[j, i] = neighbour_check(state_grid, N, i, j)
            elif state_grid[j, i] == R:
                new_mu = mu + history_grid[j, i] * mu_inc
                new_grid[j, i] = np.random.choice(
                    [S, R], p=[new_mu, 1-new_mu])

            # setting new values for the history grid
            if new_grid[j, i] == state_grid[j, i]:
                history_grid[j, i] += 1
            else:
                history_grid[j, i] = 0

    # counts the number of cells in each state and appends to
    # the corresponding list in the states dictionary
    unique, counts = np.unique(state_grid, return_counts=True)
    number = dict(zip(unique, counts/500))
    print(list(number.keys()))
    print(list(number.values()))
    for key in number:
        states[key].append(number[key])
    # replaces old grid with new one and returns it
    img.set_data(new_grid)
    state_grid[:] = new_grid[:]
    return img


def main():

    grid = state_grid(grid_size)

    # plot animated grid

    fig = plt.figure(figsize=(10, 7))

    ax = fig.add_subplot(111)
    img = ax.imshow(grid, cmap=cmap, vmin=0, vmax=4)
    ani = animation.FuncAnimation(fig, update, fargs=(img,
                                                      grid, grid_size),
                                  frames=30, interval=50, save_count=50)

    I_patch = mpatches.Patch(color='yellow', label='Susceptible')
    R_patch = mpatches.Patch(color='lightpink', label='Affected')
    D_patch = mpatches.Patch(color='seagreen', label='Recovered')
    S_patch = mpatches.Patch(color='gray', label='Dead')
    V_patch = mpatches.Patch(color='cyan', label='Vaccinated')

    plt.legend(handles=[S_patch, I_patch, R_patch,
                        D_patch, V_patch], loc=(1.1, 0.8))
    plt.axis('off')
    plt.show(ani)

    # replace with line graph and export

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111)
    ax.set_title("Cell number against time")
    ax.set_xlabel('Time')
    ax.set_ylabel('N')
    ax.set_yticklabels([])
    ax.legend(handles=[S_patch, I_patch, R_patch,
                       D_patch, V_patch])
    for key in states:
        c = plot_colors[int(key)]
        ax.plot(states[key],
                c=c, linewidth=3,
                path_effects=[pe.Stroke(linewidth=2,
                                        foreground='b'), pe.Normal()])
    os.chdir('/Users/elijoe/Documents/Online/online-comsci/Epidemiology')
    plt.savefig('line_graph.png')


# call main
if __name__ == '__main__':
    main()
