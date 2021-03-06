import numpy as np

class Doctor():

    def __init__(self, simulation, schedule, distro, decay=0):
        self.simulation = simulation
        self.schedule = np.argwhere(schedule > 0)
        if decay < 0 or decay > 1:
            raise ValueError("Decay should be positive in [0,1]")
        self.decay = decay
        self.distro = distro
        self.num_strats = 4
        self.num_drugs = simulation.treatments.shape[1]

    def change_treatment(self, t, treatment):
        if t not in self.schedule:
            raise ValueError("Doctor can only change at given times")
        other_times = self.schedule[np.where(self.schedule > t)]
        if other_times.shape[0] > 0:
            next_time = np.min(other_times)
        else:
            next_time = self.simulation.num_timesteps
        self.simulation.treatments[t: next_time, :] = treatment
        if self.decay > 0:
            for j in range(1,next_time - t):
                self.simulation.treatments[t + j :] *= max(0, self.decay ** j)

    def greedy_fittest(self, magnitude=1.0, offset=0):
        """
        Choose candidate with greatest fitness.
        :param magnitude:
        :return:
        """
        fittest_subclone = self.simulation.subclones[np.argmax([f.fitness for f in self.simulation.subclones])]
        sus_drug = np.argsort(fittest_subclone.alpha)[fittest_subclone.alpha.shape[0] - offset]
        treatment = np.zeros(self.num_drugs)
        treatment[sus_drug] = magnitude
        self.change_treatment(self.simulation.t, treatment)

    def index_action(self, magnitude=1.0, idx=0):
        treatment = np.zeros(self.num_drugs)
        treatment[idx] = magnitude
        self.change_treatment(self.simulation.t, treatment)

    def greedy_prop(self, magnitude=1.0, offset=0):
        """
        Choose candidate with greatest proportion.
        :param magnitude:
        :return:
        """
        populous_subclone = self.simulation.subclones[np.argmax([f.prop for f in self.simulation.subclones])]
        sus_drug = np.argsort(populous_subclone.alpha)[populous_subclone.alpha.shape[0] - offset]
        treatment = np.zeros(self.num_drugs)
        treatment[sus_drug] = magnitude
        self.change_treatment(self.simulation.t, treatment)

    def greedy_propweighted_fitness(self, magnitude=1.0, offset=0):
        """
        Choose candidate with greatest product of fitness and proportion.
        :param magnitude:
        :return:
        """
        weighted_subclone = self.simulation.subclones[np.argmax([f.prop * f.fitness for f in self.simulation.subclones])]
        sus_drug = np.argsort(weighted_subclone.alpha)[weighted_subclone.alpha.shape[0] - offset]
        treatment = np.zeros(self.num_drugs)
        treatment[sus_drug] = magnitude
        self.change_treatment(self.simulation.t, treatment)


    def greedy_degree(self, magnitude=1.0, offset=0):
        """
        Choose candidate with highest degree in graph, if it has any population
        :param magnitude:
        :return:
        """
        degs = [self.simulation.graph.nxgraph.degree(sc, weight="weight") * (sc.prop > 0) for sc in self.simulation.subclones]
        affected_subclone = self.simulation.subclones[np.argmax(degs)]
        sus_drug = np.argsort(affected_subclone.alpha)[affected_subclone.alpha.shape[0] - offset]
        treatment = np.zeros(self.num_drugs)
        treatment[sus_drug] = magnitude
        self.change_treatment(self.simulation.t, treatment)


    def mixed_strategy(self, mag=1.0):
        """
        This function is an example about how to simulate a doctor strategy with randomness. The deterministic case
        corresponds to choosing the strategy defined in doctor.py.
        :param distro:
        :return:
        """
        if self.distro is None:
            raise ValueError("Doctor must have a distribution specified for mixing")
        strats = {"propweight": lambda doc: doc.greedy_propweighted_fitness(magnitude=mag),
                  "prop": lambda doc: doc.greedy_prop(magnitude=mag),
                  "fit": lambda doc: doc.greedy_fittest(magnitude=mag),
                  "degree": lambda doc: doc.greedy_degree(magnitude=mag)
                  }
        if np.sum(self.distro) == 1:
            strat = np.random.choice(list(strats.keys()), 1, p=self.distro)[0]
            return strat, strats[strat]
        elif np.sum(self.distro) == 0: # do nothing on purpose
            strat = "propweight"
            return strat, lambda doc: doc.greedy_propweighted_fitness(0)
        else:
            raise ValueError("Probability vector should sum to 1")
