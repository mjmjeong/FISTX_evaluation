from modules.squat import SquatEvaluator
#from modules.benchpress import BenchpressEvaluator

def get_pose_evaluator(exercise_name='squat'):
    if exercise_name=='squat': 
        evaluator=SquatEvaluator()
    elif exercise_name=='benchpress':
        evaluator=BenchpressEvaluator()
    return evaluator
