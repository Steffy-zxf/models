# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

import paddle
import paddlenlp as ppnlp

from utils import load_vocab, generate_batch, preprocess_prediction_data

# yapf: disable
parser = argparse.ArgumentParser(__doc__)
parser.add_argument("--vocab_path", type=str, default="./senta_word_dict.txt", help="The path to vocabulary.")
parser.add_argument('--network', type=str, default="bilstm", help="Which network you would like to choose bow, lstm, bilstm, gru, bigru, rnn, birnn, bilstm_attn, cnn and textcnn?")
parser.add_argument("--params_path", type=str, default='./checkpoints/final.pdparams', help="The path of model parameter to be loaded.")
parser.add_argument("--output_path", type=str, default='./static_graph_params', help="The path of model parameter in static graph to be saved.")
args = parser.parse_args()
# yapf: enable


def main():
    # Load vocab.
    vocab = load_vocab(args.vocab_path)
    label_map = {0: 'negative', 1: 'positive'}

    # Construct the newtork.
    model = ppnlp.models.Senta(
        network=args.network, vocab_size=len(vocab), num_classes=len(label_map))

    # Load model parameters.
    state_dict = paddle.load(args.params_path)
    model.set_dict(state_dict)
    model.eval()

    inputs = [paddle.static.InputSpec(shape=[None, None], dtype="int64")]
    # Convert to static graph with specific input description
    if args.network in [
            "lstm", "bilstm", "gru", "bigru", "rnn", "birnn", "bilstm_attn"
    ]:
        inputs.append(paddle.static.InputSpec(
            shape=[None], dtype="int64"))  # seq_len

    model = paddle.jit.to_static(model, input_spec=inputs)
    # Save in static graph model.
    paddle.jit.save(model, args.output_path)


if __name__ == "__main__":
    main()
