import struct
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1 import make_axes_locatable
import paho.mqtt.client as mqtt

MQTT_SERVER = "192.168.0.45"
#MQTT_PATH = "/thermalcamera/+/image/#"
MQTT_PATH = "/ar/thermal/image"

# Initialize a list of float as per your data. Below is a random example
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# First plot: Image
im = ax1.imshow(np.random.rand(24, 32) * 30 + 10, cmap="plasma")
divider1 = make_axes_locatable(ax1)
cax1 = divider1.append_axes("right", size="5%", pad=0.05)
plt.colorbar(im, cax=cax1)

# Second plot: Trend plot
time = []
min_values = []
max_values = []
avg_values = []

line_min, = ax2.plot(time, min_values, label='Min')
line_max, = ax2.plot(time, max_values, label='Max')
line_avg, = ax2.plot(time, avg_values, label='Avg')

ax2.legend()

#fix the width of the two subpanels to be the same
plt.tight_layout()



def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)
    # The callback for when a PUBLISH message is received from the server.


def on_message(client, userdata, msg):
    global im, time, min_values, max_values, avg_values

    # more callbacks, etc
    # Create a file with write byte permission
    print(msg.payload)
    print(len(msg.payload))
    flo_arr = [
        struct.unpack("f", msg.payload[i : i + 4])[0]
        for i in range(0, len(msg.payload), 4)
    ]
    print(max(flo_arr))
    
    # Update image plot
    if im == "":
        im = ax1.imshow(
            np.array(flo_arr).reshape(24, 32), cmap="hot", interpolation="nearest",
            vmin=18,
            vmax=30,
        )
        plt.colorbar(im, cax=cax1)
    else:
        im.set_data(np.array(flo_arr).reshape(24, 32))
        im.set_clim(18,30) #min(20, min(flo_arr)), max(flo_arr))
    
    # Update trend plot
    if len(time)==0 :
        time.append(0)
    else:
        time.append(time[-1] + 1)
    min_values.append(min(flo_arr))
    max_values.append(max(flo_arr))
    avg_values.append(np.mean(flo_arr))
    # keep maximum 600 values, remove first
    if len(time) > 600:
        time.pop(0)
        min_values.pop(0)
        max_values.pop(0)
        avg_values.pop(0)

    line_min.set_data(time, min_values)
    line_max.set_data(time, max_values)
    line_avg.set_data(time, avg_values)
    ax2.relim()
    ax2.autoscale_view()

    plt.draw()


#    img = cv2.imread('img.png')
#    resized_img = cv2.resize(img, (320,240))
#    cv2.imwrite('img.png', resized_img)

# The callback for when the client receives a CONNACK response from the server.


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
# client.loop_forever()
client.loop_start()
plt.show()

