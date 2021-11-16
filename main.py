import Leap
import sys
import thread
import time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import csv
# test,,,


class SampleListener(Leap.Listener):
    row = []
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    # fields = [
    #     'frame id', 'timestamp', 'hands', ' fingers', 'tools', 'gestures',
    #     'hand type', 'hand id', 'palm position',
    #     'pitch degrees', 'roll degrees', 'yaw degrees',
    #     'arm direction', 'wrist position', 'elbow position',
    #     'finger id', 'length', 'width',
    #     'bone', 'start', 'end', 'direction',
    #     'tool id', 'position', 'direction',
    #     'gesture type', 'gesture id', 'state name', 'position/progress', 'direction/radius'
    # ]
    fields = [
        'frame id', 'timestamp', ' fingers', 'gestures',
        'palm position',
        'finger id', 'length', 'width',
        'bone', 'start', 'end', 'direction',
        'tool id', 'position', 'direction',
        'gesture type', 'gesture id', 'state name', 'position/progress', 'direction/radius'
    ]

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        self.write_to_csv(self.row)
        print "Exited"

    def on_frame(self, controller):
        data = []
        print "on frame========"
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
              frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))
        data.append(frame.id if frame.id else '')
        data.append(frame.timestamp if frame.timestamp else '')
        # data.append(len(frame.hands))
        data.append(len(frame.fingers) if frame.fingers else 0)
        # data.append(len(frame.tools))
        data.append(len(frame.gestures()))

        # Get hands
        for hand in frame.hands:
            handType = "Left hand" if hand.is_left else "Right hand"
            print "  %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position)
            # data.append(handType)
            # data.append(hand.id)
            data.append(hand.palm_position if hand.palm_position else '')
            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            # Calculate the hand's pitch, roll, and yaw angles
            print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
                direction.pitch * Leap.RAD_TO_DEG,
                normal.roll * Leap.RAD_TO_DEG,
                direction.yaw * Leap.RAD_TO_DEG)

            # data.append(direction.pitch * Leap.RAD_TO_DEG)
            # data.append(normal.roll * Leap.RAD_TO_DEG)
            # data.append(direction.yaw * Leap.RAD_TO_DEG)

            # Get arm bone
            arm = hand.arm
            print "  Arm direction: %s, wrist position: %s, elbow position: %s" % (
                arm.direction,
                arm.wrist_position,
                arm.elbow_position)

            # data.append(arm.direction)
            # data.append(arm.wrist_position)
            # data.append(arm.elbow_position)

            # Get fingers
            for finger in hand.fingers:
                print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
                    self.finger_names[finger.type],
                    finger.id,
                    finger.length,
                    finger.width)

                data.append(finger.id if finger.id else '')
                data.append(finger.length if finger.length else 0)
                data.append(finger.width if finger.width else 0)

                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    print "      Bone: %s, start: %s, end: %s, direction: %s" % (
                        self.bone_names[bone.type],
                        bone.prev_joint,
                        bone.next_joint,
                        bone.direction)
                    data.append(self.bone_names[bone.type] if self.bone_names[bone.type] else '')
                    data.append(bone.prev_joint if bone.prev_joint else '')
                    data.append(bone.next_joint if bone.next_joint else '')
                    data.append(bone.direction if bone.direction else '')

        # Get tools
        for tool in frame.tools:
            print "  Tool id: %d, position: %s, direction: %s" % (
                tool.id, tool.tip_position, tool.direction)

            data.append(tool.id if tool.id else '')
            data.append(tool.tip_position if tool.tip_position else '')
            data.append(tool.direction if tool.direction else '')

        # Get gestures
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gesture)

                # Determine clock direction using the angle between the point able and the circle normal
                if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                    clockwiseness = "clockwise"
                else:
                    clockwiseness = "counterclockwise"

                # Calculate the angle swept since the last frame
                swept_angle = 0
                if circle.state != Leap.Gesture.STATE_START:
                    previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                    swept_angle = (circle.progress - previous_update.progress) * 2 * Leap.PI

                print "  Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                        gesture.id, self.state_names[gesture.state],
                        circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)

                data.append(gesture.type if gesture.type else '')
                data.append(gesture.id if gesture.id else '')
                data.append(self.state_names[gesture.state] if self.state_names[gesture.state] else '')
                data.append(circle.progress if circle.progress else 0)
                data.append(circle.radius if circle.radius else 0)
                # data.append(swept_angle * Leap.RAD_TO_DEG)
                # data.append(clockwiseness)

            elif gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                print "  Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                        gesture.id, self.state_names[gesture.state],
                        swipe.position, swipe.direction, swipe.speed)

                data.append(gesture.type if gesture.type else '')
                data.append(gesture.id if gesture.id else '')
                data.append(self.state_names[gesture.state] if self.state_names[gesture.state] else '')
                data.append(swipe.position if swipe.position else '')
                data.append(swipe.direction if swipe.direction else '')
                # data.append(swipe.speed)

            elif gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                keytap = KeyTapGesture(gesture)
                print "  Key Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_names[gesture.state],
                        keytap.position, keytap.direction)

                data.append(gesture.type if gesture.type else '')
                data.append(gesture.id if gesture.id else '')
                data.append(self.state_names[gesture.state] if self.state_names[gesture.state] else '')
                data.append(keytap.position if keytap.position else '')
                data.append(keytap.direction if keytap.direction else '')

            elif gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                screentap = ScreenTapGesture(gesture)
                print "  Screen Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_names[gesture.state],
                        screentap.position, screentap.direction)

                data.append(gesture.type if gesture.type else '')
                data.append(gesture.id if gesture.id else '')
                data.append(self.state_names[gesture.state] if self.state_names[gesture.state] else '')
                data.append(screentap.position if screentap.position else '')
                data.append(screentap.direction if screentap.direction else '')

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print ""

        self.row.append(data)
        print('\n\n\n Size================:\n\n\n', len(self.row))
        # del data [:]

    def write_to_csv(self, row):
        with open('leap_data3.csv', 'w') as f:
            write = csv.writer(f)
            write.writerow(self.fields)
            write.writerows(row)
        print "Data stored"

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"


def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
