user_data <- read.csv("/home/cameronschloer/Code/research/HITL_Swarm_Fault_Detection/swarm_project/faultdetection-epuckswarm/data/user_study_user_data/mixed_effects_data_30.csv")

library(lme4)
library(lmerTest)

model <- lmer(Bal_Avg ~ Num_Faults + LEDS + Swarm_Size + Fault_Type1 + Fault_Type2 + (1 | Individual), data = user_data)
print(summary(model))
