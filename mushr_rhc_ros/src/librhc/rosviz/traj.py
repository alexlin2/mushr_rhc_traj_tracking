import matplotlib.cm as cm
import matplotlib.colors as colors
import rospy
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray

import torch

_traj_pub = rospy.Publisher(
    rospy.get_param("~debug/viz_rollouts/topic", "~debug/viz_rollouts"),
    MarkerArray,
    queue_size=100,
)


def viz_trajs_cmap(poses, costs, ns="trajs", cmap="gray", scale=0.03):
    max_c = torch.max(costs)
    min_c = torch.min(costs)

    norm = colors.Normalize(vmin=min_c, vmax=max_c)
    # if cmap not in cm.cmaps_listed.keys():
    #     cmap = "viridis"
    cmap = cm.get_cmap(name=cmap)

    def colorfn(cost):
        r, g, b, a = 0.0, 0.0, 0.0, 1.0
        col = cmap(norm(cost))
        r, g, b = col[0], col[1], col[2]
        if len(col) > 3:
            a = col[3]
        return r, g, b, a

    return viz_trajs(poses, costs, colorfn, ns, scale)


def viz_trajs(poses, costs, colorfn, ns="trajs", scale=0.03):
    """
        poses should be an array of trajectories to plot in rviz
        costs should have the same dimensionality as poses.size()[0]
        colorfn maps a point to an rgb tuple of colors
    """
    assert poses.shape[0] == costs.shape[0]

    markers = MarkerArray()

    for i, (traj, cost) in enumerate(zip(poses, costs)):
        m = Marker()
        m.header.frame_id = "map"
        m.header.stamp = rospy.Time.now()
        m.ns = ns + str(i)
        m.id = i
        m.type = m.LINE_STRIP
        m.action = m.ADD
        m.pose.orientation.w = 1.0
        m.scale.x = scale
        m.color.r, m.color.g, m.color.b, m.color.a = colorfn(cost)

        for t in traj:
            p = Point()
            p.x, p.y = t[0], t[1]
            m.points.append(p)

        markers.markers.append(m)

    _traj_pub.publish(markers)
