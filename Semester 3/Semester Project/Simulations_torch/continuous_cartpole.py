"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R

Continuous version by Ian Danforth
"""

import math
import gym
from gym import spaces, logger
from gym.utils import seeding
import numpy as np


class ContinuousCartPoleEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 60
    }

    def __init__(self):
        self.g = 9.81
        self.tau = 1 / self.metadata['video.frames_per_second']  # seconds between state updates
        self.nu = 13.2
        # System dynamics matrices
        self.A = np.array([
            [1, self.tau, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, self.tau],
            [0, 0, self.nu * self.tau, 1]])
        self.B = np.array([[0], [self.tau], [0], [self.nu * self.tau / self.g]])
        self.initCov = np.diag([0.1, 0.1, 0.1, 0.1])
        self.cov = 0.01 * self.initCov
        # Reward matrices
        self.Q = np.diag([1.25, 1, 12, 0.25])
        self.R = np.array([0.01])
        # Angle and displacement at which to fail the episode
        self.theta_threshold_radians = math.pi / 6
        self.x_threshold = 2.4
        # Action acceleration limits
        self.min_action = -3
        self.max_action = 3

        # Angle limit set to 2 * theta_threshold_radians so failing observation
        # is still within bounds
        high = np.array([
            self.x_threshold * 2,
            np.finfo(np.float32).max,
            self.theta_threshold_radians * 2,
            np.finfo(np.float32).max])

        self.action_space = spaces.Box(
            low=self.min_action,
            high=self.max_action,
            shape=(1,)
        )
        self.observation_space = spaces.Box(-high, high)

        self.seed()
        self.viewer = None
        self.state = None

        self.steps_beyond_done = None

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def stepPhysics(self, acceleration):
        mean = self.A @ self.state + self.B * acceleration.item()
        return self.np_random.multivariate_normal(mean.flatten(), self.cov).reshape(-1, 1)

    def step(self, action):
        assert self.action_space.contains(action), \
            "%r (%s) invalid" % (action, type(action))
        self.state = self.stepPhysics(action)
        x, x_dot, theta, theta_dot = self.state.flatten()
        done = x < -self.x_threshold \
            or x > self.x_threshold \
            or theta < -self.theta_threshold_radians \
            or theta > self.theta_threshold_radians
        done = bool(done)

        if not done:
            state_reward = (self.state.T @ self.Q @ self.state).item()
            action_reward = (action * self.R * action).item()
            reward = state_reward + action_reward
        elif self.steps_beyond_done is None:
            # Pole just fell!
            self.steps_beyond_done = 0
            reward = 0
        else:
            if self.steps_beyond_done == 0:
                logger.warn("""
You are calling 'step()' even though this environment has already returned
done = True. You should always call 'reset()' once you receive 'done = True'
Any further steps are undefined behavior.
                """)
            self.steps_beyond_done += 1
            reward = 0

        return self.state, reward, done, {}

    def reset(self):
        self.state = self.np_random.multivariate_normal(np.zeros(4), self.initCov).reshape(-1, 1)
        self.steps_beyond_done = None
        return self.state

    def render(self, mode='human'):
        screen_width = 600
        screen_height = 400

        world_width = self.x_threshold * 2
        scale = screen_width / world_width
        carty = 100  # TOP OF CART
        polewidth = 10.0
        polelen = scale * 1.0
        cartwidth = 50.0
        cartheight = 30.0

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(screen_width, screen_height)
            l, r, t, b = -cartwidth / 2, cartwidth / 2, cartheight / 2, -cartheight / 2
            axleoffset = cartheight / 4.0
            cart = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
            self.carttrans = rendering.Transform()
            cart.add_attr(self.carttrans)
            self.viewer.add_geom(cart)
            l, r, t, b = -polewidth / 2, polewidth / 2, polelen-polewidth / 2, -polewidth / 2
            pole = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
            pole.set_color(.8, .6, .4)
            self.poletrans = rendering.Transform(translation=(0, axleoffset))
            pole.add_attr(self.poletrans)
            pole.add_attr(self.carttrans)
            self.viewer.add_geom(pole)
            self.axle = rendering.make_circle(polewidth / 2)
            self.axle.add_attr(self.poletrans)
            self.axle.add_attr(self.carttrans)
            self.axle.set_color(.5, .5, .8)
            self.viewer.add_geom(self.axle)
            self.ball = rendering.make_circle(15)
            # self.balltrans = rendering.Transform(translation=(0, axleoffset + polelen))
            # self.ball.add_attr(self.balltrans)
            # self.ball.add_attr(self.carttrans)
            # self.ball.set_color(.5, .5, .8)
            # self.viewer.add_geom(self.ball)
            self.track = rendering.Line((0, carty), (screen_width, carty))
            self.track.set_color(0, 0, 0)
            self.viewer.add_geom(self.track)

        if self.state is None:
            return None

        x = self.state
        cartx = x[0] * scale + screen_width / 2.0  # MIDDLE OF CART
        self.carttrans.set_translation(cartx, carty)
        self.poletrans.set_rotation(-x[2])
        # self.balltrans.set_translation()

        return self.viewer.render(return_rgb_array=(mode == 'rgb_array'))

    def close(self):
        if self.viewer:
            self.viewer.close()
