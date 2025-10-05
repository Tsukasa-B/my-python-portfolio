import torch
import math
import argparse

from isaaclab.app import AppLauncher

# --- コマンドライン引数の設定 ---
parser = argparse.ArgumentParser(description="Standalone test for the Porcaro robot with TorqueActionController.")
parser.add_argument("--headless", action="store_true", help="Run simulation in headless mode.")
# --scene 引数を追加し、動作パターンを選択できるようにする
parser.add_argument(
    "--scene", type=int, default=0,
    help="Select the test scene to run (0-4). "
         "0: Wrist sine wave (Default), "
         "1: DF muscle sine wave, "
         "2: F muscle sine wave, "
         "3: G muscle sine wave, "
         "4: G muscle step pressure"
)
args, unknown = parser.parse_known_args()

# --- AppLauncherの初期化 ---
launcher = AppLauncher(headless=args.headless)
simulation_app = launcher.app

# --- Isaac LabのAPIを新しいパスでインポート ---
from isaaclab.sim import SimulationContext
from isaaclab.assets import Articulation
from isaaclab.terrains import TerrainImporter

# --- あなたのプロジェクトのモジュールをインポート ---
from .porcaro_rl_env_cfg import PorcaroRLEnvCfg
from .actions.torque import TorqueActionController

def main():
    """ Isaac Lab環境でTorqueActionControllerを直接テストするメイン関数 """

    # 1. 環境設定を読み込む
    cfg = PorcaroRLEnvCfg(num_envs=1)

    # 2. シミュレーションコンテキストを作成
    sim = SimulationContext(cfg.sim)

    # 3. シーンのアセットをスポーンさせる
    terrain = TerrainImporter(cfg.terrain)
    robot = Articulation(cfg.scene.robot)
    drum_stand = Articulation(cfg.scene.drum_stand)

    sim.reset()
    print("-----------------------------------------")
    print("Scene and assets have been initialized.")
    print(f"Running Test Scene: {args.scene}")
    print("-----------------------------------------")

    # 4. TorqueActionControllerのインスタンスを作成
    dt_ctrl = cfg.sim.dt * cfg.decimation
    action_controller = TorqueActionController(
        dt_ctrl=dt_ctrl,
        r=0.014, L=0.150,
        Pmax=0.6,
    )
    action_controller.reset(n_envs=1, device=sim.device)

    wrist_ids, _ = robot.find_joints(r"Base_link_Wrist_joint")
    grip_ids, _ = robot.find_joints(r"Hand_link_Grip_joint")
    wrist_id = wrist_ids[0]
    grip_id = grip_ids[0]
    print(f"Targeting Wrist Joint ID: {wrist_id}, Grip Joint ID: {grip_id}")

    # 5. シミュレーションループを開始
    while simulation_app.is_running():
        if sim.is_running():
            sim.render()

        if sim.is_playing():
            sim.step()

            root_state = robot.data.root_state_w
            root_pos = root_state[:, 0:3]
            joint_pos = robot.data.joint_pos

            if sim.step_count % 100 == 0:
                print(f"Step: {sim.step_count} | Joint Pos: {joint_pos.cpu().numpy()[0]}")

            # (B) 選択されたシーンに基づいて指令値を生成
            sim_time = sim.current_time
            # アクションのデフォルト値（全筋肉OFF）
            action_df, action_f, action_g = -1.0, -1.0, -1.0
            
            # 圧力P [MPa] からアクションa [-1, 1] への変換関数
            def pressure_to_action(p_mpa, p_max=0.6):
                # P = (a + 1) * 0.5 * P_max  => a = P / (0.5 * P_max) - 1
                return p_mpa / (0.5 * p_max) - 1.0

            if args.scene == 0:
                # シーン0: 手首のsin波運動（DFとFが拮抗）
                # 圧力は 0 ~ 0.6MPa の間で変化
                pressure = (math.sin(2.0 * math.pi * 0.5 * sim_time) + 1.0) * 0.5 * 0.6
                action_df = pressure_to_action(pressure)
                action_f = pressure_to_action(0.6 - pressure) # 拮抗筋は逆の圧力
                action_g = -1.0 # GはOFF

            elif args.scene == 1:
                # シーン1: DF筋（背屈）のみsin波で加圧
                pressure = (math.sin(2.0 * math.pi * 0.5 * sim_time) + 1.0) * 0.5 * 0.6
                action_df = pressure_to_action(pressure)

            elif args.scene == 2:
                # シーン2: F筋（屈曲）のみsin波で加圧
                pressure = (math.sin(2.0 * math.pi * 0.5 * sim_time) + 1.0) * 0.5 * 0.6
                action_f = pressure_to_action(pressure)

            elif args.scene == 3:
                # シーン3: G筋（握り）のみsin波で加圧
                pressure = (math.sin(2.0 * math.pi * 0.5 * sim_time) + 1.0) * 0.5 * 0.6
                action_g = pressure_to_action(pressure)

            elif args.scene == 4:
                # シーン4: G筋（握り）を0.1MPaずつの階段状に加圧
                step_duration = 2.0  # 2秒ごとに圧力を変更
                pressure_level = math.floor(sim_time / step_duration)
                pressure = min(pressure_level * 0.1, 0.6) # 0.1MPaずつ、最大0.6MPaまで
                action_g = pressure_to_action(pressure)
                if sim.step_count % 100 == 0:
                    print(f"  Current Grip Pressure Command: {pressure:.2f} MPa")

            actions = torch.tensor([[action_df, action_f, action_g]], device=sim.device)

            # (C) コントローラを実行してトルクを計算・適用
            action_controller.apply(
                actions=actions,
                q=joint_pos,
                robot=robot,
                joint_ids=(wrist_id, grip_id)
            )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        launcher.close()
        print("Simulation has been closed.")

