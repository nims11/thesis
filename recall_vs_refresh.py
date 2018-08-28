import sys
import os
import colorsys
import matplotlib.pyplot as plt

def get_random_color(i, n):
    hue = (360//n*i)/360.0
    sat = 0.5
    light = 0.5
    r,g,b = colorsys.hls_to_rgb(hue, light, sat)
    return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

qrel = sys.argv[1]
dirs = sys.argv[2:]

rel_counts = {}
with open(qrel) as f:
    for line in f:
        topic, _, _, rel = line.strip().split()
        if int(rel) > 0:
            rel_counts[topic] = rel_counts.get(topic, 0) + 1

del rel_counts["athome106"]

labels = []
plt.suptitle('Average Recall vs # of Refresh', fontsize=15, fontweight='bold')

R_arr = {}
k = 25
ps = [-1, 0.4, 0.6, 0.8, 1.0]
if len(labels) == 0:
    labels = dirs
for idx, (dir, label, p) in enumerate(zip(dirs, labels, ps)):
    culm_arrs = {}
    color = get_random_color(idx, len(dirs))
    for topic, R in rel_counts.items():
        buffer = []
        buffer_sum = 0
        total_rel = 0;
        culm_arrs[topic] = [0]
        with open(os.path.join(dir, topic)) as f:
            for line in f:
                _, rel = line.strip().split()
                if int(rel) > 0:
                    rel = 1
                else:
                    rel = 0
                total_rel += rel
                if p == -1:
                    culm_arrs[topic].append(total_rel/rel_counts[topic])
                    continue
                buffer.append(rel)
                buffer_sum += rel
                if len(buffer) > k:
                    buffer_sum -= buffer[0]
                    buffer = buffer[1:]
                if rel == 0 and buffer_sum / k < p:
                    culm_arrs[topic].append(total_rel/rel_counts[topic])
        if len(culm_arrs[topic]) > 1000:
            culm_arrs[topic] = culm_arrs[topic][:1000]

    R_arr[dir] = []
    R = 0
    x_vals = list(range(len(culm_arrs[topic])))
    y_vals = [sum(vals)/len(vals) for vals in zip(*list(culm_arrs.values()))]

    plt.plot(x_vals, y_vals, color=color, label=dir, linewidth=1.0, alpha=0.7)

plt.xlabel('# of Refresh')
plt.ylabel('Recall')
ax = plt.subplot(111)
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
             box.width, box.height * 0.9])
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
      fancybox=True, shadow=True, ncol=3)

plt.savefig('a.pdf', bbox_inches="tight")

print(R, ' '.join(dirs))
R = 0
for idx in range(len(R_arr[dir])):
    print(R, ' '.join(['%.3f' % (R_arr[dir][idx]) for dir in dirs]))
    R += 0.1
