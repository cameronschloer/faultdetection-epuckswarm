import random
import fire
import random
import os


def generate(size, seed, fault, task, length=300, num_faulty=1, led_bins=0, lower=0, upper=1000, headless=False):
	if num_faulty > size or num_faulty < 0:
		raise ValueError(f"`num_faulty` must be between 0 and {size}")
	show_leds = "true"
	if led_bins == 0:
		show_leds = "false"
		led_bins = 2 # need a default value that is not 0

	headless_pre = headless_suf = ''
	if headless:
		headless_pre = '<!--'
		headless_suf = "-->"

		
	if size == 16 or size == 20:
		arena_length = 3.0
		arena = f"""
    <!-- *********************** -->
    <!-- * Arena configuration * -->
    <!-- *********************** -->

    <arena size="3.5, 3.5, 2" center="0,0,1">

        <floor id="floor"
            source="loop_functions"
            pixels_per_meter="50" />

        <box id="wall_north" size="3,0.1,0.5" movable="false">
        <body position="0,1.5,0" orientation="0,0,0" />
        </box>
        <box id="wall_south" size="3,0.1,0.5" movable="false">
        <body position="0,-1.5,0" orientation="0,0,0" />
        </box>
        <box id="wall_east" size="0.1,3,0.5" movable="false">
        <body position="1.5,0,0" orientation="0,0,0" />
        </box>
        <box id="wall_west" size="0.1,3,0.5" movable="false">
        <body position="-1.5,0,0" orientation="0,0,0" />
        </box>

        <distribute>
        <position method="uniform" min="-1.5,-1.5,0" max="1.5,1.5,0" />
        <orientation method="uniform" min="0,0,0" max="360,0,0" />
        <entity quantity="{size}" max_trials="5">
            <e-puck id="ep" rab_data_size="1000" rab_range="1">    <!-- using a high bandwidth of 1000 bytes for now -->
            <controller config="ehs" />
            </e-puck>
        </entity>
        </distribute>

    </arena>                                  
    """

	elif size == 64: 
		arena_length = 6.0
		arena = f"""    
    <!-- *********************** -->
    <!-- * Arena configuration * -->
    <!-- *********************** -->

    <arena size="6, 6, 2" center="0,0,1">

        <floor id="floor"
            source="loop_functions"
            pixels_per_meter="50" />

        <box id="wall_north" size="6,0.1,0.5" movable="false">
        <body position="0,3,0" orientation="0,0,0" />
        </box>
        <box id="wall_south" size="6,0.1,0.5" movable="false">
        <body position="0,-3,0" orientation="0,0,0" />
        </box>
        <box id="wall_east" size="0.1,6,0.5" movable="false">
        <body position="3,0,0" orientation="0,0,0" />
        </box>
        <box id="wall_west" size="0.1,6,0.5" movable="false">
        <body position="-3,0,0" orientation="0,0,0" />
        </box>

        <distribute>
        <position method="uniform" min="-3,-3,0" max="3,3,0" />
        <orientation method="uniform" min="0,0,0" max="360,0,0" />
        <entity quantity="{size}" max_trials="5">
            <e-puck id="ep" rab_data_size="1000" rab_range="1">    <!-- using a high bandwidth of 1000 bytes for now -->
            <controller config="ehs" />
            </e-puck>
        </entity>
        </distribute>

    </arena>
    """

	else:
		raise ValueError("Give valid size, 16 or 64")
	
	id_faulty = random.sample(range(size), num_faulty)
	faulty_times = random.choices(range(lower, upper), k=num_faulty)

	id_faulty_str = ' '.join(map(str, id_faulty))
	faulty_times_str = ' '.join(map(str, faulty_times))

	content = f"""<?xml version="1.0" ?>

  <!-- *************************************************** -->
  <!-- * A fully commented XML is diffusion_1.xml. Refer * -->
  <!-- * to it to have full information about what       * -->
  <!-- * these options mean.                             * -->
  <!-- *************************************************** -->

  <argos-configuration>

  <!-- ************************* -->
  <!-- * General configuration * -->
  <!-- ************************* -->
  <!-- length in seconds -->
  <framework>
      <system threads="0" />
      <experiment length="{length}"
                  ticks_per_second="10"
                  random_seed="{seed}" /> 
  </framework>

  <!-- *************** -->
  <!-- * Controllers * -->
  <!-- *************** -->
  <!-- time_between_robots_trans_behav is in seconds -->
  <controllers>

      <epuck_homswarm_controller id="ehs"
                                  library="build/controllers/epuck_hom_swarm/libepuck_hom_swarm.so">
      <actuators>
          <differential_steering implementation="default"  noise_std_dev="0.1" />
          <leds implementation="default" medium="leds" />
          <range_and_bearing implementation="default" />
      </actuators>
      <sensors>
          <proximity implementation="default" show_rays="false" />
          <range_and_bearing implementation="medium" medium="rab" show_rays="false" noise_std_dev="0.01" />
          <differential_steering implementation="default" vel_noise_range="-0.1:0.1"  dist_noise_range="-1.0:1.0" />
      </sensors>
      <params>
          <experiment_run swarm_behavior="{task}"
              swarm_behavior_trans=""
              time_between_robots_trans_behav="-1.0"
              fault_behavior="{fault}" 
                      id_faulty_robot="15" />
          <wheel_turning max_speed="5" />
      </params>
      </epuck_homswarm_controller>

  </controllers>

  <!-- ****************** -->
  <!-- * Loop functions * -->
  <!-- ****************** -->
  <loop_functions library="build/loop_functions/homswarm_loop_functions/libhomswarm_loop_functions.so"
                  label="homswarm_loop_functions">
      <params  output="nohup_{task}_{seed}.txt" 
          arenalength="{arena_length}"/>

  </loop_functions>

  {arena}

  <!-- ******************* -->
  <!-- * Physics engines * -->
  <!-- ******************* -->
  <physics_engines>
      <dynamics2d id="dyn2d" iterations="50" />
  </physics_engines>

  <!-- ********* -->
  <!-- * Media * -->
  <!-- ********* -->
  <media>
      <range_and_bearing id="rab" />
      <led id="leds" />
  </media>

  <!-- ****************** -->
  <!-- * Visualization * -->
  <!-- ****************** -->
  <visualization>
      <qt-opengl>
      <camera>
          <placements>
          <placement index="0" position="1.99925,-0.0942354,11.1666" look_at="1.77948,-0.0942354,10.191" up="-0.975552,2.07473e-15,0.219767" lens_focal_length="65" />
          </placements>
      </camera>
      <user_functions library="build/loop_functions/id_loop_functions/libid_loop_functions"
                      label="id_qtuser_functions" /> 
      </qt-opengl>
      <!-- <user_functions label="homswarm_qt_user_functions" /> -->
  </visualization>

  </argos-configuration>
  """

	with open(f"epuck_{task}_{seed}.argos", 'w') as out:
		out.write(content)

if __name__ == "__main__":
    fire.Fire(generate)