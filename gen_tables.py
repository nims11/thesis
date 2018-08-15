import os
import numpy as np

datasets = ['athome1', 'athome2', 'athome3', 'athome4']
strategies = ['exponential', 'static', 'partial', 'precision', 'recency']
parameters = {
    'exponential': [''],
    'static': ['k=1', 'k=100', 'k=1,it=100', 'k=1,it=1000', 'k=1,it=10000', 'k=1,it=100000'],
    'partial': ['k=10,s=1000', 'k=100,s=100', 'k=100,s=500', 'k=100,s=1000', 'k=100,s=5000', 'k=500,s=1000'],
    'precision': ['p=%s,m=25' % x for x in ['0.4', '0.6', '0.8', '1.0']],
    'recency': ['w=%d,it=1000' % w for w in [1,5,10,25]]
}

METRICS = [
    'Total Scoring Time',
    'Total Training Time',
    'Total Running Time',
    '0.75 Running Time',
    '0.75 Effort',
    'Recall at 1',
    'Recall at 1.5',
    'Recall at 2'
]

topics = {}
data = {}
for dataset in datasets:
    data[dataset] = {}
    results_path = 'results.'+dataset
    topics[dataset] = {}

    with open(os.path.join(results_path, 'qrels')) as qrel:
        for line in qrel:
            topic, _, doc, rel = line.strip().split()
            if topic not in topics[dataset]:
                topics[dataset][topic] = {'rels': 0}
            topics[dataset][topic]['rels'] += (1 if int(rel) > 0 else 0)

    for strategy in strategies:
        print(dataset, strategy)
        data[dataset][strategy] = {}
        strategy_path = os.path.join(results_path, strategy)
        for parameter in parameters[strategy]:
            label = strategy
            if parameter:
                label += '(' + parameter + ')'
            data[dataset][strategy][parameter] = {'label': label}
            metrics = data[dataset][strategy][parameter]
            # Gather metrics
            with open(os.path.join(strategy_path, parameter, 'log')) as logfile:
                for line in logfile.read().splitlines()[-20:]:
                    if '=' in line:
                        key, val = line.strip().split('=')
                        key = key.strip()
                        val = val.strip()
                        if key in METRICS:
                            metrics[key] = float(val)
            assert(len(metrics) == 9)
            # Gather gain curve statistics
            topic_gain_curves = {}
            topic_eff_75 = {}
            for topic in topics[dataset]:
                topic_gain_curves[topic] = [0]
                num_rels = topics[dataset][topic]['rels']
                with open(os.path.join(strategy_path, parameter, topic)) as f:
                    for line in f:
                        _, rel = line.strip().split()
                        if int(rel) > 0:
                            rel = 1
                        else:
                            rel = 0
                        topic_gain_curves[topic].append(topic_gain_curves[topic][-1] + rel)
                        if topic not in topic_eff_75 and topic_gain_curves[topic][-1] >= 0.75 * num_rels:
                            topic_eff_75[topic] = len(topic_gain_curves[topic]) / num_rels
                topic_gain_curves[topic] = [r/num_rels for r in topic_gain_curves[topic]]
                if topic not in topic_eff_75:
                    topic_eff_75[topic] = 2 / metrics['Recall at 2'] * 0.75
            metrics['r1'] = [topic_gain_curves[topic][int(1 * topics[dataset][topic]['rels'])] for topic in topics[dataset]]
            metrics['r1.5'] = [topic_gain_curves[topic][int(1.5 * topics[dataset][topic]['rels'])] for topic in topics[dataset]]
            metrics['r2'] = [topic_gain_curves[topic][int(1.99 * topics[dataset][topic]['rels'])] for topic in topics[dataset]]

            gain_curve_x = []
            gain_curve_y = []
            R = 0
            while R < 2.01:
                gain_curve_x.append(R)
                y_val = 0
                for topic in topic_gain_curves:
                    y_val += topic_gain_curves[topic][int(max(R-0.01, 0) * topics[dataset][topic]['rels'])]
                y_val /= len(topic_gain_curves)
                gain_curve_y.append(y_val)
                R += 0.1
            metrics['gain_curve'] = (np.array(gain_curve_x), np.array(gain_curve_y))
            metrics['0.75 Effort'] = sum(topic_eff_75.values()) / len(topic_eff_75)


average = {}
for strategy in strategies:
    average[strategy] = {}
    for parameter in parameters[strategy]:
        average[strategy][parameter] = {}
        for metric in METRICS:
            average[strategy][parameter][metric] = 0
            for dataset in datasets:
                average[strategy][parameter]['label'] = data[dataset][strategy][parameter]['label']
                average[strategy][parameter][metric] += data[dataset][strategy][parameter][metric]
            average[strategy][parameter][metric] /= len(datasets)
        average[strategy][parameter]['label'] = data[dataset][strategy][parameter]['label']
        average[strategy][parameter]['gain_curve'] = sum(data[dataset][strategy][parameter]['gain_curve'][1] for dataset in datasets) / len(datasets)
        average[strategy][parameter]['gain_curve'] = (data[datasets[0]][strategy][parameter]['gain_curve'][0], average[strategy][parameter]['gain_curve'])


def to_table_row(data, strategy, parameter):
    label = strategy
    if parameter:
        label += '(' + parameter + ')'
    label = '\\texttt{%s}' % label
    vals = []
    for metric in ['Recall at 1', 'Recall at 1.5', 'Recall at 2', '0.75 Effort', ]:
        vals.append('%.3f' % data[strategy][parameter][metric])
    for metric in ['Total Running Time']:
        vals.append('%.2f' % (data[strategy][parameter][metric]/60000))

    return ' & '.join([label] + vals) + ' \\\\ \\hline'

def to_table(dataset):
    lines = []
    for strategy in strategies:
        for parameter in parameters[strategy]:
            lines.append(to_table_row(dataset, strategy, parameter))
        lines[-1] = lines[-1] + ' \\hline'
    return '\n'.join(lines)

import matplotlib.pyplot as plt
markers = ['s', 'o', '^', 'x']
markersizes = [7,5,5, 5]

for idx, d in enumerate([average['exponential'][''], average['static']['k=1'], average['static']['k=100']]):
    x_vals, y_vals = d['gain_curve']
    plt.plot(x_vals, y_vals, label=d['label'], linewidth=1.0, marker=markers[idx], markersize=markersizes[idx])

plt.xlabel('Effort')
plt.ylabel('Avg. Recall')
ax = plt.subplot(111)
box = ax.get_position()
ax.legend(loc='lower right', shadow=True)
plt.savefig('./plots/bmi_static.pdf', bbox_inches="tight")
plt.close()


for idx, d in enumerate([average['static']['k=1'], average['partial']['k=10,s=1000'], average['partial']['k=500,s=1000']]):
    x_vals, y_vals = d['gain_curve']
    plt.plot(x_vals, y_vals, label=d['label'], linewidth=1.0, marker=markers[idx], markersize=markersizes[idx])

plt.xlabel('Effort')
plt.ylabel('Avg. Recall')
ax = plt.subplot(111)
box = ax.get_position()
ax.legend(loc='lower right', shadow=True)
plt.savefig('./plots/static_partial.pdf', bbox_inches="tight")
plt.close()

for idx, d in enumerate([average['partial']['k=100,s=1000'], average['partial']['k=100,s=5000'], average['partial']['k=100,s=100']]):
    x_vals, y_vals = d['gain_curve']
    plt.plot(x_vals, y_vals, label=d['label'], linewidth=1.0, marker=markers[idx], markersize=markersizes[idx])

plt.xlabel('Effort')
plt.ylabel('Avg. Recall')
ax = plt.subplot(111)
box = ax.get_position()
ax.legend(loc='lower right', shadow=True)
plt.savefig('./plots/partial2.pdf', bbox_inches="tight")
plt.close()


for idx, d in enumerate([average['precision']['p=1.0,m=25'], average['precision']['p=0.8,m=25'], average['precision']['p=0.4,m=25']]):
    x_vals, y_vals = d['gain_curve']
    plt.plot(x_vals, y_vals, label=d['label'], linewidth=1.0, marker=markers[idx], markersize=markersizes[idx])

plt.xlabel('Effort')
plt.ylabel('Avg. Recall')
ax = plt.subplot(111)
box = ax.get_position()
ax.legend(loc='lower right', shadow=True)
plt.savefig('./plots/precision.pdf', bbox_inches="tight")
plt.close()


for idx, d in enumerate([average['static']['k=1,it=100000'], average['static']['k=1,it=10000'], average['static']['k=1,it=1000'], average['static']['k=1,it=100']]):
    x_vals, y_vals = d['gain_curve']
    plt.plot(x_vals, y_vals, label=d['label'], linewidth=1.0, marker=markers[idx], markersize=markersizes[idx])

plt.xlabel('Effort')
plt.ylabel('Avg. Recall')
ax = plt.subplot(111)
box = ax.get_position()
ax.legend(loc='lower right', shadow=True)
plt.savefig('./plots/training.pdf', bbox_inches="tight")
plt.close()


for idx, d in enumerate([average['static']['k=1,it=1000'], average['static']['k=1,it=100000'], average['recency']['w=25,it=1000'] ]):
    x_vals, y_vals = d['gain_curve']
    plt.plot(x_vals, y_vals, label=d['label'], linewidth=1.0, marker=markers[idx], markersize=markersizes[idx])

plt.xlabel('Effort')
plt.ylabel('Avg. Recall')
ax = plt.subplot(111)
box = ax.get_position()
ax.legend(loc='lower right', shadow=True)
plt.savefig('./plots/recency.pdf', bbox_inches="tight")
plt.close()
