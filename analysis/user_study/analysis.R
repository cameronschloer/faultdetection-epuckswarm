user_data <- read.csv("/home/cameronschloer/Code/research/HITL_Swarm_Fault_Detection/swarm_project/faultdetection-epuckswarm/data/user_study_user_data/mixed_effects_data.csv")

library(lme4)
library(lmerTest)

swarm_size_f = factor(user_data$Swarm_Size)
Num_Faults_f = factor(user_data$Num_Faults)

# user_data_faults <- subset(user_data, Num_Faults != "0")
# user_data_faults$Num_Faults_f <- factor(user_data_faults$Num_Faults_f)
# user_data_faults$Wheel_Fault  <- factor(user_data_faults$Wheel_Fault)
# user_data_faults$Prox_Fault   <- factor(user_data_faults$Prox_Fault)
# user_data_faults$swarm_size_f <- factor(user_data_faults$swarm_size_f)
# user_data_faults$LEDS         <- factor(user_data_faults$LEDS)
# user_data_faults$Num_Faults <- droplevels(user_data_faults$Num_Faults)

# user_data_no_faults <- subset(user_data, Num_Faults == "0")
# user_data_no_faults$Num_Faults_f <- factor(user_data_no_faults$Num_Faults_f)
# user_data_no_faults$Wheel_Fault  <- factor(user_data_no_faults$Wheel_Fault)
# user_data_no_faults$Prox_Fault   <- factor(user_data_no_faults$Prox_Fault)
# user_data_no_faults$swarm_size_f <- factor(user_data_no_faults$swarm_size_f)
# user_data_no_faults$LEDS         <- factor(user_data_no_faults$LEDS)
# user_data_no_faults$Num_Faults <- droplevels(user_data_no_faults$Num_Faults)



model <- lmer(
  Bal_Avg ~ (Num_Faults_f + LEDS + swarm_size_f + Wheel_Fault + Prox_Fault)
            # + Num_Faults_f:swarm_size_f
            # - Num_Faults_f:LEDS:Wheel_Fault
            # - Num_Faults_f:swarm_size_f:Wheel_Fault
            # - Num_Faults_f:LEDS:Prox_Fault
            # - Num_Faults_f:swarm_size_f:Prox_Fault
            # - Num_Faults_f:LEDS:swarm_size_f
            # - LEDS:swarm_size_f:Prox_Fault
            + (1 | Individual),
  data = user_data
)

# model <- lmer(
#   Bal_Avg ~ (Num_Faults + LEDS + Swarm_Size + Wheel_Fault + Prox_Fault)
#             # + Num_Faults_f:swarm_size_f
#             # - Num_Faults_f:LEDS:Wheel_Fault
#             # - Num_Faults_f:swarm_size_f:Wheel_Fault
#             # - Num_Faults_f:LEDS:Prox_Fault
#             # - Num_Faults_f:swarm_size_f:Prox_Fault
#             # - Num_Faults_f:LEDS:swarm_size_f
#             # - LEDS:swarm_size_f:Prox_Fault
#             + (1 | Individual),
#   data = user_data_faults
# )

# model <- lmer(
#   Bal_Avg ~ (LEDS + Swarm_Size + Wheel_Fault + Prox_Fault)
#             # + Num_Faults_f:swarm_size_f
#             # - Num_Faults_f:LEDS:Wheel_Fault
#             # - Num_Faults_f:swarm_size_f:Wheel_Fault
#             # - Num_Faults_f:LEDS:Prox_Fault
#             # - Num_Faults_f:swarm_size_f:Prox_Fault
#             # - Num_Faults_f:LEDS:swarm_size_f
#             # - LEDS:swarm_size_f:Prox_Fault
#             + (1 | Individual),
#   data = user_data_no_faults
# )

# model <- lmer(Bal_Avg ~ (Num_Faults_f + LEDS + swarm_size_f + Wheel_Fault + Prox_Fault)^3 + (1 | Individual), data = user_data)
# model <- lmer(Bal_Avg ~ Num_Faults_f * LEDS * swarm_size_f * Wheel_Fault * Prox_Fault + (1 | Individual), data = user_data)
# model <- lmer(Bal_Avg ~ Num_Faults_f + LEDS + swarm_size_f + Fault_Type1 + Fault_Type2 + (1 | Individual), data = user_data)
print(summary(model))

citation("lme4")
