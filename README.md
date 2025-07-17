# BlastZone
BlastZone is an interactive shooting game where players aim and shoot swiming ducks using a custom-built gun controller. The controller is equipped with an MPU-6500 6-Axis Gyroscope and Accelerometer Sensor Module, enabling real-time motion tracking.

The controller isn’t built yet because the sensor used (MPU-6500) doesn’t have a magnetometer, which is necessary to keep track of an absolute position. Currently, the controller can only track changes in angle, which isn’t ideal. To counter this problem, I have implemented a high-pass filter so that the crosshair eventually always returns to the center. However, this is not a long-term solution because the user now has to "fight against" the pull toward the center. If the crosshair isn’t pulled back to the center, the controller and crosshair would desynchronize, making the game unplayable. A magnetometer (included in the MPU-9250), fused with the gyroscope data, would solve this problem once and for all.

![game](https://github.com/user-attachments/assets/de4d5af9-2a36-443b-8463-90823369bffc)
![IMG_3435](https://github.com/user-attachments/assets/8cd13ca1-a658-4def-adda-5367f21950d8)
