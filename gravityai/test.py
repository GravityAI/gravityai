from . import pipelineOrchestration

def test_pipeline(container_list, keys_list, metadata_dicts, input_file):
    pipeline = pipelineOrchestration.GravityAIPipeline(container_list, keys_list, metadata_dicts)
    result = pipeline.run(input_file)
    return result