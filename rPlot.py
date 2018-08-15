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

labels = []
plt.suptitle('Average Recall vs Effort', fontsize=15, fontweight='bold')

R_arr = {}
eff_at_75 = {}
if len(labels) == 0:
    labels = dirs

def beautify(label):
    if '/' in label:
        label = label.replace('/', '(')
        label += ')'
    return label


markers = ['s', 'o', '^', 'x']
markersizes = [7,5,5, 5]
for idx, (dir, label) in enumerate(zip(dirs, labels)):
    culm_arrs = {}
    color = get_random_color(idx, len(dirs))
    eff_at_75[dir] = {}
    for topic, R in rel_counts.items():
        culm_arrs[topic] = [0]
        with open(os.path.join(dir, topic)) as f:
            for line in f:
                try:
                    _, rel = line.strip().split()
                except:
                    print(line)
                    continue
                if int(rel) > 0:
                    rel = 1
                else:
                    rel = 0
                culm_arrs[topic].append(culm_arrs[topic][-1] + rel)
                if topic not in eff_at_75[dir] and culm_arrs[topic][-1] >= 0.75 * rel_counts[topic]:
                    eff_at_75[dir][topic] = len(culm_arrs[topic]) / rel_counts[topic]
    eff_at_75[dir] = sum(eff_at_75[dir].values()) / len(eff_at_75[dir])
    R_arr[dir] = []
    R = 0
    x_vals = []
    while R < 2.0:
        x_vals.append(R)
        R_arr[dir].append(sum(culm_arrs[topic][int(rel_counts[topic]*R)]/rel_counts[topic] for topic in culm_arrs)/len(culm_arrs))
        R += 0.1
    line2d = plt.plot(x_vals, R_arr[dir], label=beautify(dir), linewidth=1.0, marker=markers[idx], markersize=markersizes[idx])

plt.xlabel('Effort')
plt.ylabel('Avg. Recall')
ax = plt.subplot(111)
box = ax.get_position()
# ax.set_position([box.x0, box.y0 + box.height * 0.1,
#              box.width, box.height * 0.9])
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
      # fancybox=True, shadow=True, ncol=2)
ax.legend(loc='lower right', shadow=True)

plt.savefig('a.pdf', bbox_inches="tight")
# plt.show()

# print(R, ' '.join(dirs))
# R = 0
# for idx in range(len(R_arr[dir])):
#     if abs(R-1) < 0.01 or abs(R - 1.5) < 0.01 or abs(R - 2.0) < 0.01:
#         print(' '.join(['%.3f' % (R_arr[dir][idx]) for dir in dirs]), '&', end=" ")
#     R += 0.1

for dir in dirs:
    print('%.3f' % eff_at_75[dir])
