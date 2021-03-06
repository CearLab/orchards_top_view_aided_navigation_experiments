import os
import shutil
import json

from framework import utils
from content.leftovers.trunks_detection_old_exp import TrunksDetectionExperiment

############################################################################################################################
#                                                    CONFIGURATION AREA                                                    #
############################################################################################################################
altitude = 80
repetitions = 1
grid_size_values = [6]

from content.data_pointers.lavi_april_18.dji import snapshots_80_meters as snapshots
# from content.data_pointers.lavi_november_18.dji import plot1_snapshots_80_meters as snapshots
# from content.data_pointers.lavi_november_18.dji import plot2_snapshots_80_meters as snapshots

from content.data_pointers.lavi_april_18.orchard_topology import plot_pattern
# from content.data_pointers.lavi_november_18.orchard_topology import plot1_pattern as plot_pattern
# from content.data_pointers.lavi_november_18.orchard_topology import plot2_pattern as plot_pattern

############################################################################################################################

if __name__ == '__main__':
    execution_dir = utils.create_new_execution_folder('trunks_detection')
    image_key_to_best_score = {}
    for image_key in snapshots.keys():
        image_descriptor = snapshots[image_key]

        for grid_size in grid_size_values:

            # Run experiment
            experiment = TrunksDetectionExperiment(name='trunks_detection_on_%s' % image_key, data_sources=image_descriptor.path, working_dir=execution_dir,
                                                   params={'crop_ratio': 0.8, 'initial_sigma_to_dim_y_ratio': 0.33, 'grid_size_for_optimization': grid_size,
                                                           'orchard_pattern': plot_pattern}, metadata={'image_key': image_key, 'altitude': altitude})
            experiment.run(repetitions, viz_mode=False)

            # Post processing (image level)
            semantic_images_dir = os.path.join(experiment.experiment_dir, 'semantic_trunk_images')
            os.makedirs(semantic_images_dir)
            repetition_to_score = {}
            for repetition in experiment.valid_repetitions:
                shutil.copy(os.path.join(experiment.experiment_dir, str(repetition), 'refined_semantic_trunks.jpg'), os.path.join(semantic_images_dir, '%d.jpg' % repetition))
                repetition_to_score[repetition] = experiment.summary['results'][repetition]['pattern_match_score']
                with open(os.path.join(experiment.experiment_dir, 'scores.json'), 'w') as f:
                    json.dump(repetition_to_score, f, indent=4)
            sorted_repetitions_by_score = [key for key, value in sorted(repetition_to_score.iteritems(), key=lambda (k, v): v, reverse=True)]
            for i_th, repetition in enumerate(sorted_repetitions_by_score):
                os.rename(os.path.join(semantic_images_dir, '%s.jpg' % repetition), os.path.join(semantic_images_dir, '%d_[repetition_%d].jpg' % (i_th + 1, repetition)))
            if len(sorted_repetitions_by_score) > 0:
                image_key_to_best_score[experiment.experiment_dir] = repetition_to_score[sorted_repetitions_by_score[0]]

    # Post processing (execution level)
    best_scores_summary = sorted(image_key_to_best_score.iteritems(), key=lambda (k, v): v, reverse=True)
    with open(os.path.join(execution_dir, 'best_scores.json'), 'w') as f:
        json.dump(best_scores_summary, f, indent=4)

    # TODO: in the runner play with N, crop_ratio, initial_sigma_to_dim_y, maybe also with the pattern??