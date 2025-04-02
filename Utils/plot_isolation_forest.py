import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.tree import export_graphviz
import pydotplus

def visualize_isolation_tree(model, features,
                             output_path='C:/Users/anand/Downloads/Projects/Crash Detection '
                                         'System/Detection_model_mobile/isolation_forest_tree_visualization1.png'):
    """
    visualize a single decision tree from an Isolation Forest model.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    estimator = model.estimators_[0]
    dot_data = export_graphviz(
        estimator,
        out_file=None,
        feature_names=features,
        filled=True,
        rounded=True,
        special_characters=True
    )
    graph = pydotplus.graph_from_dot_data(dot_data)
    graph.write_png(output_path)
    print(f"Isolation Tree visualization saved to:{output_path}")

def plot_isolation_feature_importance(model, features,
                                      output_path='C:/Users/anand/Downloads/Projects/Crash Detection '
                                                  'System/Detection_model_mobile/isolation_forest_feature_importance1.png'):
    """
    Plot average feature importance across all trees in an Isolation Forest model.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    importance =np.mean(
        [tree.feature_importances_ for tree in model.estimators_],
        axis=0
    )

    plt.figure(figsize=(10, 6))
    plt.barh(features, importance)
    plt.xlabel(' Average Feature Importance')
    plt.ylabel('Feature')
    plt.title('Feature Importance in Isolation Forest')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()
    print(f"Feature importance plot saved to:{output_path}")
