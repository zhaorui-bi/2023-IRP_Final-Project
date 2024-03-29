import cv2
import numpy as np
import math

left = []
right = []
forward = []


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def Intersection_calculations(A, B, C, D): # Calculate intersections
    """
    Function to calculate intersection point between two lines given four points A, B, C, and D.

    Parameters:
        - A (Point): First point of the first line (x, y)
        - B (Point): Second point of the first line (x, y)
        - C (Point): First point of the second line (x, y)
        - D (Point): Second point of the second line (x, y)

    Returns:
        - Point: Intersection point of the two lines (x, y)
    """
    # Line AB represented as a1x + b1y = c1
    a1 = B.y - A.y
    b1 = A.x - B.x
    c1 = a1*(A.x) + b1*(A.y)
    # Line CD represented as a2x + b2y = c2
    a2 = D.y - C.y
    b2 = C.x - D.x
    c2 = a2*(C.x) + b2*(C.y)
    judgment = a1*b2 - a2*b1
    if (judgment == 0):
        return Point(10**9, 10**9)
    else:
        global X,Y
        x = (b2*c1 - b1*c2)/judgment
        y = (a1*c2 - a2*c1)/judgment
        return Point(x, y)


def are_lists_equal(list1, list2):# Check whether the two lists are equal
    """
       Function to check if two lists are equal.

       Parameters:
           - list1 (list): First list
           - list2 (list): Second list

       Returns:
           - bool: True if the lists are equal, False otherwise
       """
    if len(list1) != len(list2):
        return False
    for i in range(len(list1)):
        if list1[i] != list2[i]:
            return False
    return True
def Horizontal_angle(x1, y1, x2, y2)->float:
    # Calculate the horizontal angle
    slope = (y2 - y1) / (x2 - x1)
    Horizontal_radians = math.atan(slope)
    Horizontal_degrees = math.degrees(Horizontal_radians)
    return Horizontal_degrees

def vertical_angle(x1, y1, x2, y2)->float:
    # Calculate the vertical angle
    slope = (y2 - y1) / (x2 - x1)
    vertical_radians = math.atan(1 / slope)
    vertical_degrees = math.degrees(vertical_radians)
    return vertical_degrees

def detect_path(first_frame, mask):
    # Convert frames to HSV color space
#     hsv_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2HSV)
#     # Create a mask of the blue area based on the threshold
#     lower_blue = np.array([99, 30, 30])
#     upper_blue = np.array([130, 255, 255])
#     mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
#     mask = cv2.erode(mask, None, iterations=2)
#     mask = cv2.dilate(mask, None, iterations=2)
    # Extract the blue part from the original frame
    Blue_frame = cv2.bitwise_and(first_frame, first_frame, mask=mask)
    # Convert the extracted image to a grayscale map
    final_frame = cv2.cvtColor(Blue_frame, cv2.COLOR_BGR2GRAY)
    # Perform edge detection on the processed image
    edges = cv2.Canny(final_frame, 60, 110)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=40, minLineLength=30, maxLineGap=300)
    # Draw the detected straight lines
#     cv2.imshow('Line Detection', first_frame)
#     cv2.imshow('Final', edges)
    if lines is not None:
        parallel = None
        vertical = None
        judge = [False, False, False]
        list1 = [True,True,True]  # cross
        list2 = [True,True,False]  # T
        list3 = [False,True,False]  # Right
        list4 = [True,False,False]  # Left
        list5 = [False,True,True]  # Right T
        list6 = [True,False,True] # Left T
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Calculate the slope
            if x1 == x2:
                k = np.inf
            else:
                k = float(abs(y2-y1)/abs(x2-x1))
            if parallel is not None and vertical is not None:
                break
            elif vertical is None and k > 1.6:
                vertical = line[0]
                cv2.putText(first_frame, f'Vertical Angle:{vertical_angle(vertical[0],vertical[1],vertical[2],vertical[3])}',
                            (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0,0,255), 2)
            elif parallel is None and 0 < k < 1.6:
                parallel = line[0]
                cv2.putText(first_frame, f'Horizontal Angle:{Horizontal_angle(parallel[0],parallel[1],parallel[2],parallel[3])}',
                            (200, 70), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0,255,0), 2)
        # Draw the detected vertical and horizontal lines
        if vertical is not None:
            x1, y1, x2, y2 = vertical
            cv2.line(first_frame, (x1, y1), (x2, y2), (0,255,0), 2)
        if parallel is not None:
            x1, y1, x2, y2 = parallel
            cv2.line(first_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        # If a vertical and horizontal line is detected, their intersection is calculated
        if parallel is not None and vertical is not None:
            A = Point(parallel[0], parallel[1])
            B = Point(parallel[2], parallel[3])
            C = Point(vertical[0], vertical[1])
            D = Point(vertical[2], vertical[3])
            intersection = Intersection_calculations(A, B, C, D)
            X = intersection.x
            Y = intersection.y
            distance = math.sqrt((X-480) ** 2 + (Y-360) ** 2)
            cv2.putText(first_frame,f'Distance:{distance}',
                        (200, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 0, 0), 2)
            if parallel[0] < parallel[2]:
                left = parallel[:2]
                right = parallel[2:]
            else:
                left = parallel[2:]
                right = parallel[:2]
            if vertical[1] < vertical[3]:
                forward = vertical[:2]
            else:
                forward = vertical[2:]

            distance1 = math.sqrt((left[0] - X) ** 2 + (left[1] - Y) ** 2)
            distance2 = math.sqrt((right[0] - X) ** 2 + (right[1] - Y) ** 2)
            distance3 = math.sqrt((forward[0] - X) ** 2 + (forward[1] - Y) ** 2)
            # Determine the type of line segment detected based on the distance
#             print(distance1)
#             print(distance2)
#             print(distance3)
            if distance1 > 100:
                judge[0] = True
            if distance2 > 100:
                judge[1] = True
#             if distance3 > 100:
#                 judge[2] = True
#             if are_lists_equal(judge, list1):
#                 print("It is cross.")
#                 return 'crossroad'
#             elif are_lists_equal(judge, list2):
#                 print("It is T.")
#                 return 'T'
            if are_lists_equal(judge, list3):
                
                return 'right'
            elif are_lists_equal(judge, list4):
                
                return 'left'
#             elif are_lists_equal(judge, list5):
#                 print("It is right T.")
#                 return 'rightT'
#             elif are_lists_equal(judge, list6):
#                 print("It is left T.")
#                 return 'leftT'
        elif parallel is None and vertical is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if math.sqrt((x1 - x2) ** 2 + (y1 - x2) ** 2) <= 120:
                    
                    return 'short'
                    cv2.putText(first_frame, f'Short Distance:{math.sqrt((x1 - x2) ** 2 + (y1 - x2) ** 2)}',
                                (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 2)
                else:
    
                    return 'long'
