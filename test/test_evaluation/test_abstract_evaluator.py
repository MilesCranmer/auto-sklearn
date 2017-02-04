# -*- encoding: utf-8 -*-
from __future__ import print_function
import os
import shutil
import sys
import unittest
import unittest.mock

import numpy as np

from autosklearn.util import backend

this_directory = os.path.dirname(__file__)
sys.path.append(this_directory)
from evaluation_util import get_multiclass_classification_datamanager
from autosklearn.evaluation import AbstractEvaluator


class AbstractEvaluatorTest(unittest.TestCase):
    _multiprocess_can_split_ = True

    def test_finish_up_model_predicts_NaN(self):
        '''Tests by handing in predictions which contain NaNs'''
        rs = np.random.RandomState(1)
        D = get_multiclass_classification_datamanager()
        output_dir = os.path.join(
            os.getcwd(), '.test_finish_up_model_predicts_NaN')

        try:
            shutil.rmtree(output_dir)
        except:
            pass

        backend_api = backend.create(output_dir, output_dir)
        ae = AbstractEvaluator(Datamanager=D, backend=backend_api,
                               output_y_test=False)
        ae.Y_optimization = rs.rand(33, 3)
        predictions_ensemble = rs.rand(33, 3)
        predictions_test = rs.rand(25, 3)
        predictions_valid = rs.rand(25, 3)

        # NaNs in prediction ensemble
        predictions_ensemble[5, 2] = np.NaN
        _, loss, _, additional_run_info = ae.finish_up(
            0.1, predictions_ensemble, predictions_valid, predictions_test)
        self.assertEqual(loss, 1.0)
        self.assertEqual(additional_run_info, 'Model predictions for '
                                              'optimization set contains NaNs.')

        # NaNs in prediction validation
        predictions_ensemble[5, 2] = 0.5
        predictions_valid[5, 2] = np.NaN
        _, loss, _, additional_run_info = ae.finish_up(
            0.1, predictions_ensemble, predictions_valid, predictions_test)
        self.assertEqual(loss, 1.0)
        self.assertEqual(additional_run_info, 'Model predictions for '
                                              'validation set contains NaNs.')

        # NaNs in prediction test
        predictions_valid[5, 2] = 0.5
        predictions_test[5, 2] = np.NaN
        _, loss, _, additional_run_info = ae.finish_up(
            0.1, predictions_ensemble, predictions_valid, predictions_test)
        self.assertEqual(loss, 1.0)
        self.assertEqual(additional_run_info, 'Model predictions for '
                                              'test set contains NaNs.')

        self.assertEqual(len(os.listdir(os.path.join(output_dir,
                                                   '.auto-sklearn'))), 0)

    @unittest.mock.patch('autosklearn.util.backend.Backend')
    def test_disable_file_output(self, backend_mock):
        rs = np.random.RandomState(1)
        D = get_multiclass_classification_datamanager()

        ae = AbstractEvaluator(Datamanager=D, backend=backend_mock,
                               output_y_test=False, disable_file_output=True)

        predictions_ensemble = rs.rand(33, 3)
        predictions_test = rs.rand(25, 3)
        predictions_valid = rs.rand(25, 3)

        loss_, additional_run_info_ = ae.file_output(
            0.1, predictions_ensemble, predictions_valid, predictions_test)

        self.assertIsNone(loss_)
        self.assertIsNone(additional_run_info_)
        # This function is not guarded by a an if statement
        self.assertEqual(backend_mock.save_predictions_as_npy.call_count, 0)
