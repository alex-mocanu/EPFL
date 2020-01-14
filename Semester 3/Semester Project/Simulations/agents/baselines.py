import numpy as np


def get_baseline(env, agent, cfg):
    '''
    Retunr the desired type of baseline
    :param cfg: configurations for the baseline to use
    '''
    if cfg.type == 'average':
        return AverageBaseline(env, agent, cfg.num_trajectories)
    elif cfg.type == 'state':
        return StateBaseline(env, agent, cfg.num_trajectories)
    elif cfg.type == 'optimal_const':
        return OptimalConstBaseline(env, agent, cfg.num_trajectories)
    elif cfg.type == 'optimal_state':
        return OptimalStateBaseline(env, agent, cfg.num_trajectories)
    return ZeroBaseline(env, agent, cfg.num_trajectories)


def generate_trajectories(env, agent, curr_state, remaining_steps, traj, prob, all_traj):
    '''
    Generate all possible trajectories for the environment
    :param env: environment for which we generate the trajectories
    :param agent: agent which interacts with the envronment
    :param curr_state: current state of the environment
    :param remaining_steps: number of steps left
    :param traj: current trajectory
    :param prob: current probability of the trajectory
    :param all_traj: trajectories accumulator
    '''
    if remaining_steps == 0:
        all_traj.append((traj, prob))
        return

    for action in range(env.num_actions):
        for state in range(env.num_states):
            new_prob = prob * agent._pi[curr_state,action] * env._p[curr_state,action,state]
            new_traj = traj.copy()
            new_traj.append((curr_state, action, env._mean_r[curr_state, action]))
            generate_trajectories(env, agent, state, remaining_steps - 1, new_traj, new_prob, all_traj)


def compute_returns(trajectories, discounts):
    '''
    Compute the returns at each step in an array of trajectories
    :param trajectories: array of trajectories
    :param discounts: discounting factors at each step
    '''
    rewards = np.array([[r for _,_,r in traj] for traj in trajectories])
    return np.flip(np.flip(discounts * rewards).cumsum(axis=1))


class Baseline:
    def __init__(self, env, agent, num_trajectories):
        self.env = env
        self.agent = agent
        self.num_trajectories = num_trajectories
        self.discounts = np.array([self.agent.gamma**step for step in range(self.env.episode_length)])

    def compute(self, exact=False):
        '''
        Compute the baseline for the current policy
        :param exact: whether to compute the exact baseline value
        '''
        if exact:
            self._exact_compute()
        else:
            self._mc_compute()

    def get_baseline(self, trajectory):
        '''
        Get the baseline values for a given trajectory
        :param trajectory: trajectory for which we request the baseline
        '''
        raise NotImplementedError

    def _exact_compute(self):
        '''
        Compute the exact value of the baseline
        '''
        raise NotImplementedError

    def _mc_compute(self):
        '''
        Compute the baseline by sampling trajectories
        '''
        raise NotImplementedError


class ZeroBaseline(Baseline):
    def compute(self, exact=False):
        pass

    def get_baseline(self, trajectory):
        return np.array([0])


class AverageBaseline(Baseline):
    def compute(self, exact=False):
        if exact:
            self._exact_compute()
        else:
            self._mc_compute()

    def _exact_compute(self):
        # Generate trajectories
        trajectories = []
        for init_state in range(self.env.num_states):
            generate_trajectories(self.env, self.agent, init_state,
                self.env.episode_length, [], 1 / self.env.num_states, trajectories)
        returns = compute_returns([t[0] for t in trajectories], self.discounts)
        probs = [t[1] for t in trajectories]
        self.baseline = np.average(returns, axis=0, weights=probs)

    def _mc_compute(self):
        returns = np.zeros(self.env.episode_length)
        for _ in range(self.num_trajectories):
            self.env.reset()
            obs = self.env.get_state()
            for step in range(self.env.episode_length):
                action = self.agent.action(obs)
                obs, reward, done, _ = self.env.step(action)
                returns[step] += reward
        returns /= self.num_trajectories
        self.baseline = np.flip(np.flip(self.discounts * returns).cumsum())

    def get_baseline(self, trajectory):
        return self.baseline


class StateBaseline(Baseline):
    def __init__(self, env, agent, num_trajectories):
        super(StateBaseline, self).__init__(env, agent, num_trajectories)
        self.baseline = np.zeros((self.env.episode_length, self.env.num_states))
        self.steps = list(range(self.env.episode_length))

    def _exact_compute(self):
        # Generate trajectories
        trajectories = []
        for init_state in range(self.env.num_states):
            generate_trajectories(self.env, self.agent, init_state,
                self.env.episode_length, [], 1 / self.env.num_states, trajectories)
        returns = compute_returns([t[0] for t in trajectories], self.discounts)
        probs = [t[1] for t in trajectories]
        state_probs = np.zeros_like(self.baseline)
        for i in range(len(trajectories)):
            for step in range(self.env.episode_length):
                state = trajectories[i][0][step][0]
                self.baseline[step,state] += returns[i,step] * trajectories[i][1]
                state_probs[step,state] += trajectories[i][1]
        self.baseline /= state_probs

    def _mc_compute(self):
        for start_step in range(self.env.episode_length):
            for start_state in range(self.env.num_states):
                for _ in range(self.num_trajectories):
                    self.env.reset()
                    self.env.set_state(start_state)
                    obs = start_state
                    rewards = np.zeros(self.env.episode_length - start_step)
                    for step in range(start_step, self.env.episode_length):
                        action = self.agent.action(obs)
                        obs, reward, _, _ = self.env.step(action)
                        rewards[step - start_step] = reward
                    self.baseline[start_step,start_state] += (self.discounts[start_step:] * rewards).sum()
        # Normalize baseline values
        self.baseline /= self.num_trajectories

    def get_baseline(self, trajectory):
        states = [int(state) for state,_,_ in trajectory]
        return self.baseline[self.steps, states]


class OptimalConstBaseline(Baseline):
    def __init__(self, env, agent, num_trajectories):
        super(OptimalConstBaseline, self).__init__(env, agent, num_trajectories)
        self.grad_dim = self.env.num_features * self.env.num_actions

    def _exact_compute(self):
        # Generate trajectories
        trajectories = []
        for init_state in range(self.env.num_states):
            generate_trajectories(self.env, self.agent, init_state,
                self.env.episode_length, [], 1 / self.env.num_states, trajectories)
        returns = compute_returns([t[0] for t in trajectories], self.discounts)
        # Expand dimension for returns to cover all gradient components
        returns = np.tile(np.expand_dims(returns, axis=2), self.grad_dim)
        square_grads = np.array([[self.agent._policy_log_grad(s, a).flatten() for s,a,_ in traj[0]] for traj in trajectories])**2
        probs = [t[1] for t in trajectories]
        self.baseline = np.average(square_grads * returns, axis=0, weights=probs) / np.average(square_grads, axis=0, weights=probs)

    def _mc_compute(self):
        returns = np.zeros((self.num_trajectories, self.env.episode_length))
        grads = np.zeros((self.num_trajectories, self.env.episode_length, self.grad_dim))
        for ep in range(self.num_trajectories):
            self.env.reset()
            obs = self.env.get_state()
            for step in range(self.env.episode_length):
                action = self.agent.action(obs)
                grads[ep,step] = self.agent._policy_log_grad(obs, action).flatten()
                obs, reward, done, _ = self.env.step(action)
                returns[ep,step] = reward
        returns = np.flip(np.flip(self.discounts *  returns, axis=1).cumsum(axis=1), axis=1)
        # Expand dimension for returns to cover all gradient components
        returns = np.tile(np.expand_dims(returns, axis=2), self.grad_dim)
        square_grads = grads**2
        self.baseline = (square_grads * returns).mean(axis=0) / square_grads.mean(axis=0)

    def get_baseline(self, trajectory):
        return self.baseline


class OptimalStateBaseline(Baseline):
    def __init__(self, env, agent, num_trajectories):
        super(OptimalStateBaseline, self).__init__(env, agent, num_trajectories)
        self.grad_dim = self.env.num_features * self.env.num_actions
        self.baseline = np.zeros((self.env.episode_length, self.env.num_states, self.grad_dim))
        self.steps = list(range(self.env.episode_length))
        # Compute policy log gradients for all state-action combinations
        self.all_grads = np.array([[self.agent._policy_log_grad(state, action).flatten()
            for action in range(self.env.num_actions)]
            for state in range(self.env.num_states)])

    def _exact_compute(self):
        # Generate trajectories
        trajectories = []
        for init_state in range(self.env.num_states):
            generate_trajectories(self.env, self.agent, init_state,
                self.env.episode_length, [], 1 / self.env.num_states, trajectories)
        returns = compute_returns([t[0] for t in trajectories], self.discounts)
        # Expand dimension for returns to cover all gradient components
        returns = np.tile(np.expand_dims(returns, axis=2), self.grad_dim)
        square_grads = np.array([[self.agent._policy_log_grad(s, a).flatten() for s,a,_ in traj[0]] for traj in trajectories])**2
        probs = [t[1] for t in trajectories]
        state_square_grads = np.zeros_like(self.baseline)
        for i in range(len(trajectories)):
            for step in range(self.env.episode_length):
                state = trajectories[i][0][step][0]
                self.baseline[step,state] += square_grads[i,step] * returns[i,step] * probs[i]
                state_square_grads[step,state] += square_grads[i,step] * probs[i]
        self.baseline /= state_square_grads

    def _mc_compute(self):
        for start_step in range(self.env.episode_length):
            for start_state in range(self.env.num_states):
                grads, returns = [], []
                for _ in range(self.num_trajectories):
                    self.env.reset()
                    self.env.set_state(start_state)
                    obs = start_state
                    rewards = np.zeros(self.env.episode_length - start_step)
                    for step in range(start_step, self.env.episode_length):
                        action = self.agent.action(obs)
                        if step == start_step:
                            grads.append(self.all_grads[start_state,action])
                        obs, reward, _, _ = self.env.step(action)
                        rewards[step - start_step] = reward
                    returns.append((self.discounts[start_step:] * rewards).sum())
                # Compute baseline
                square_grads, returns = np.array(grads)**2, np.array(returns).reshape(-1,1)
                self.baseline[start_step,start_state] = (square_grads * returns).mean(axis=0) / square_grads.mean(axis=0)

    def get_baseline(self, trajectory):
        states = [int(state) for state,_,_ in trajectory]
        return self.baseline[self.steps, states]
