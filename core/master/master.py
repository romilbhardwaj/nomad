class Master(object):
    def __init__(self, universe):
        self.universe = universe
        profile_cluster()
    def profile_cluster():
        create_profiling_containers()
        wait_for_profiling_completion()

    def submit_network_profiling(self, network_profiling_info):
        self.universe.update_network_profiling(network_profiling_info)

    def submit_pipeline_profiling(self, pipeline_profiling_info):
        self.universe.update_pipeline_profiling(pipeline_profiling_info)

    def create_profiling_containers(self):
        pass

    def wait_for_profiling_completion(self):
        pass

    def submit_pipeline(self, pipeline):
        self.universe.add_pipline(pipeline)
        self.profile_pipeline(pipeline)
        scheduling_result = self.scheduler.schedule(pipeline)
        self.universe.save_scheduling_decision(scheduling_result)
        self.instantiate_pipeline(pipeline)

    def profile_pipeline(self, pipeline):
        create_pipeline_profiling_containers()
        wait_for_pipeline_profiling_completion()
        pass







