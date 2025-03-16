from modules.squat import SquatEvaluator

def get_pose_evaluator(exercise_name='squat'):
    if exercise_name=='squat': 
        evaluator=SquatEvaluator()
    elif exercise_name=='benchpress':
        evaluator=bench_evaluator()
    return evaluator
