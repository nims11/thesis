import os

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
            data[dataset][strategy][parameter] = {}
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
            assert(len(metrics) == 8)
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
                try:
                    for topic in topic_gain_curves:
                        y_val += topic_gain_curves[topic][int(R * topics[dataset][topic]['rels'])]
                except:
                    break
                y_val /= len(topic_gain_curves)
                gain_curve_y.append(y_val)
                R += 0.1
            metrics['gain_curve'] = (gain_curve_x, gain_curve_y)
            metrics['0.75 Effort'] = sum(topic_eff_75.values()) / len(topic_eff_75)


average = {}
for strategy in strategies:
    average[strategy] = {}
    for parameter in parameters[strategy]:
        average[strategy][parameter] = {}
        for metric in METRICS:
            average[strategy][parameter][metric] = 0
            for dataset in datasets:
                average[strategy][parameter][metric] += data[dataset][strategy][parameter][metric]
            average[strategy][parameter][metric] /= len(datasets)


def to_table_row(data, strategy, parameter):
    label = strategy
    if parameter:
        label += '(' + parameter + ')'
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

def plot(curves)
