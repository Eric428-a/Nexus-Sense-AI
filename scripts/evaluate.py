"""Evaluation entrypoint."""
from nexus.reasoning.evaluator import ReasoningEvaluator
def main(): print(ReasoningEvaluator().evaluate(score=0.8,evidence_count=2))
if __name__=="__main__": main()
