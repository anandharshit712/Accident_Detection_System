from graphviz import Digraph

dot = Digraph(format='png')
dot.attr(rankdir='TB')

dot.node('input', 'Input\n(B, 16, 3, 224, 224)')
dot.node('resnet', 'ResNet-18\n(B*16, 512)')
dot.node('reshape', 'Reshape\n(B, 16, 512)')
dot.node('lstm', 'LSTM\n(B, 16, 128)')
dot.node('fc', 'Fully Connected\n(B, 1)')
dot.node('sigmoid', 'Sigmoid\nOutput: Accident / No Accident')

dot.edges([('input', 'resnet'),
           ('resnet', 'reshape'),
           ('reshape', 'lstm'),
           ('lstm', 'fc'),
           ('fc', 'sigmoid')])

dot.render('model_block_diagram', view=True)
