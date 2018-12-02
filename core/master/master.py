from core.placement.minlatsolver import RecMinLatencySolver
class Master(object):
    def __init__(self, universe):
        self.universe = universe
        #profile_cluster()
        self.scheduler = RecMinLatencySolver(universe.get_graph())

    def profile_cluster():
        create_profiling_containers()
        wait_for_profiling_completion()

    def submit_network_profiling(self, network_profiling_info):
        self.universe.update_network_profiling(network_profiling_info)

    def submit_pipeline_profiling(self, pid, pipeline_profiling_info):
        self.universe.update_pipeline_profiling(pid, pipeline_profiling_info)

    def create_profiling_containers(self):
        pass

    def wait_for_profiling_completion(self):
        pass

    def submit_pipeline(self, fns, start, end):
        pipeline_id = self.universe.add_pipeline(fns, start, end)
        pipeline_profiling_info = self.profile_pipeline(self.universe.get_pipeline(pipeline_id))
        self.submit_pipeline_profiling(pipeline_id, pipeline_profiling_info)
        self.schedule(pipeline_id)
        status = self.instantiate_pipeline(pipeline_id)
        return pipeline_id if status != -1 else -1

    def schedule(self, pipeline_id):
        pipeline = self.universe.get_pipeline(pipeline_id)
        start, end = pipeline.start_node, pipeline.end_node
        operators = [self.universe.get_operator(oid) for oid in pipeline.operators]
        #run scheduler
        latency, placement, distribution = self.scheduler.find_optimal_placement(start, end, operators)
        #create opertor instances
        print(placement)

    def profile_pipeline(self, pipeline):
        #create_pipeline_profiling_containers()
        #wait_for_pipeline_profiling_completion()

        # fill in cloud_exec_time and msg_size
        pipeline_profiling_info = []
        for op_id in pipeline.operators:
            profiling_info = {}
            profiling_info['id'] = op_id
            profiling_info['ref_exec_time'] = 10
            profiling_info['output_msg_size'] = 20
            pipeline_profiling_info.append(profiling_info)

        return pipeline_profiling_info








