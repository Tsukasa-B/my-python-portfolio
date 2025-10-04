import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from Isaaclab.managers import SceneEntityCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass
from isaaclab.sensors import ContactSensorCfg

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" #Path(__file__)このファイルのある場所をオブジェクトでとる．resolve()絶対パスにして迷子にならない．parents[2]/"assets"２つ上の階層のassetsフォルダに入る
ROBOT_USD = str(ASSETS_DIR / "porcaro.usd")  #命名したASSETS_DIRのなかにあるusdファイルを取得し命名
DRUM_USD  = str(ASSETS_DIR / "sneadrum.usd")
DRUMSTAND_USD  = str(ASSETS_DIR / "sneadrumstand.usd")

# --- ロボットの設定 ---
ROBOT_CFG = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",  # /World/envs/env_.* の部分は省略可能
    spawn=sim_utils.UsdFileCfg(
        usd_path=ROBOT_USD,
    ),
    # ここにロボットのアクチュエータ設定を追加します (例)
    actuators={
        "pam_actuators": ImplicitActuatorCfg(
            joint_names_expr=[".*"], # 全ての関節に適用する場合
            stiffness=0.0,
            damping=10.0,
            effort_limit=1000.0,
        )
    }
)

# --- ドラムの設定 ---
DRUM_CFG = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Drum",
    spawn=sim_utils.UsdFileCfg(
        usd_path=DRUM_USD,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=True, # 重力無効化
        ),
    ),
    # 関節を固定（フリーズ）して動かないようにするための設定
    actuators={
        "freeze_joints": ImplicitActuatorCfg(
            joint_names_expr=[".*"],
            stiffness=1.0e6,
            damping=1.0e5,
        )
    },
)

# --- ドラムスタンドの設定 ---
DRUMSTAND_CFG = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/DrumStand",
    spawn=sim_utils.UsdFileCfg(
        usd_path=DRUMSTAND_USD,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=True, # 重力無効化
        ),
    ),
    # こちらも関節を固定
    actuators={
        "freeze_joints": ImplicitActuatorCfg(
            joint_names_expr=[".*"],
            stiffness=1.0e6,
            damping=1.0e5,
        )
    },
)





@configclass
class PorcaroRLEnvCfg(DirectRLEnvCfg):
    # env
    episode_length_s = 5.0
    decimation = 4
    action_scale = 1
    action_space = 3
    observation_space = 5
    state_space = 0

    # simulation 
    sim: SimulationCfg = SimulationCfg(
        dt=1 / 200,
        render_interval=1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,            
        )
    )
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    contact_sensor: ContactSensorCfg = ContactSensorCfg(
        prim_path="/World/envs/env_.*/Robot/.*",  # Path to base_link in cloned envs
        history_length=5,
        update_period=0.005,  # Matches sim dt = 1/200
        track_air_time=True,  # Not needed for base
    )

    # scene
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=32,
        env_spacing=3.0, # アセットが干渉しないように十分な距離を確保
        replicate_physics=True
    )

    # --- 3. シーンにアセットを追加し、位置を調整 ---
    # ここで先ほど定義したアセット設定をクラスの属性として追加します。
    # Isaac Labは自動的にこれらのアセットをシーンに読み込みます。

    # ロボットを原点(0, 0, 0)に配置
    robot: ArticulationCfg = ROBOT_CFG

    # ドラムスタンドを (x=0.5, y=0, z=0) に配置
    drum_stand: ArticulationCfg = DRUMSTAND_CFG.replace(
        spawn=sim_utils.UsdFileCfg(
            usd_path=DRUMSTAND_USD,
            rigid_props=DRUMSTAND_CFG.spawn.rigid_props,
            # ここで位置と向きを指定
            init_state=AssetCfg.InitialStateCfg(
                pos=(0.5, 0.0, 0.0), # (x, y, z)
                rot=(1.0, 0.0, 0.0, 0.0), # (w, x, y, z)
            )
        )
    )

    # ドラムをドラムスタンドの上あたり (x=0.5, y=0, z=0.5) に配置
    # 注意：このZ座標はUSDの原点に依存するため、実際のモデルに合わせて調整が必要です。
    drum: ArticulationCfg = DRUM_CFG.replace(
        spawn=sim_utils.UsdFileCfg(
            usd_path=DRUM_USD,
            rigid_props=DRUM_CFG.spawn.rigid_props,
            init_state=AssetCfg.InitialStateCfg(
                pos=(0.5, 0.0, 0.5), # (x, y, z)
                rot=(1.0, 0.0, 0.0, 0.0), # (w, x, y, z)
            )
        )
    )

    # events
    events: EventCfg = EventCfg()

    # robot


    #reward