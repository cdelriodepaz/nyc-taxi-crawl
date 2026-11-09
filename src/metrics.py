from sklearn.metrics import average_precision_score, precision_score, recall_score


def score_model(name, y_true, y_pred, y_score):
    pr_auc = average_precision_score(y_true, y_score)
    return {
        "model": name,
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred),
        "pr_auc": pr_auc,
        "lift": pr_auc / y_true.mean(),
    }