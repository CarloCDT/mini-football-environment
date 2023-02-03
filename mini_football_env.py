from abc import ABC, abstractmethod
from mlagents_envs.base_env import ActionTuple
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.environment import UnityEnvironment
import numpy as np

class UnityEnvironmentAbstract(ABC):
    @abstractmethod
    def step(action):
        pass

    @abstractmethod
    def reset():
        pass

    @abstractmethod
    def close():
        pass

class MiniFootballEnv(UnityEnvironmentAbstract):
    def __init__(self, path='./mini_football_windows/Mini Football Environment.exe'):
        self.channel = EngineConfigurationChannel()
        self.env = UnityEnvironment(path, seed=42, side_channels=[self.channel])
        self.state = None

        self.env.step()
        self.behavior_name = list(self.env.behavior_specs)[0]
        
        self.reset()

    def step(self, action):

        terminated = False
        truncated = False
        info = None
        step_reward = 0

        transformed_action = ActionTuple(np.array(action[:2]).reshape(1,2).astype(np.float32), np.array(action[-1]).reshape(1,1).astype(np.float32))

        self.env.set_actions(behavior_name=self.behavior_name, action=transformed_action)
        self.env.step()

        decision_steps, terminal_steps = self.env.get_steps(self.behavior_name)
        step_reward += decision_steps.reward[0]

        for agent_id in terminal_steps:
            step_reward += terminal_steps.reward[0]
            terminated = True

        if not terminated:
            observation = decision_steps.obs[0][0]
            
        else:
            observation = []
            #self.reset()
        
        self.state = observation

        return observation, step_reward, terminated, truncated, info

    def reset(self):
        self.env.reset()
        self.env.step()
        decision_steps, terminal_steps = self.env.get_steps(self.behavior_name)
        self.state = decision_steps.obs[0][0]

    def close(self):
        pass

    def set_channel_params(self, width, height, quality_level, time_scale, target_frame_rate, capture_frame_rate):
        self.channel.set_configuration_parameters(
            width= width,
            height= height,
            quality_level= quality_level,
            time_scale= time_scale,
            target_frame_rate= target_frame_rate,
            capture_frame_rate= capture_frame_rate,
            )