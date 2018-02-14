import tensorflow as tf


class model(object):
    def __init__(
        self,
        dict_size,
        unroll_len=50,
        depth=3,
        hidden_size=512,
    ):
        # with tf.device("/cpu:0"):
            """
                X: [batch_size, unroll_len]
                emb: [batch_size, unroll_len, hidden_size]
                logits_over_time: [unroll_len, batch_size, dict_size]
                final_logits: [batch_size, unroll_len, dict_size]
                result: [batch_size, unroll_len]
            """
            self.dict_size = dict_size
            self.depth = depth
            self.hidden_size = hidden_size
            self.unroll_len = unroll_len
            self.learning_rate = tf.placeholder_with_default(0.5, shape=None)
            self.X = tf.placeholder(tf.int64, [None, self.unroll_len], "X")
            self.batch_size = tf.shape(self.X)[0]
            self.input_mask = tf.placeholder_with_default(
                input=tf.ones([self.batch_size, self.unroll_len]),
                shape=[None, self.unroll_len],
                name="input_mask",
            )
            self.Y = tf.placeholder(tf.int64, [None, self.unroll_len], "Y")
            self.output_mask = tf.placeholder_with_default(
                input=tf.ones([self.batch_size, self.unroll_len]),
                shape=[None, self.unroll_len],
                name="output_mask",
            )
            self.embeddings = tf.Variable(
                tf.random_normal([self.dict_size, self.hidden_size]),
            )
            embedded_in = tf.nn.embedding_lookup(self.embeddings, self.X)

            lstms = [
                tf.contrib.rnn.BasicLSTMCell(self.hidden_size)
                for _ in range(self.depth)
            ]
            cell = tf.contrib.rnn.MultiRNNCell(lstms)

            state = cell.zero_state(self.batch_size, tf.float32)
            logits_over_time = []

            self.ans_fully_W = tf.Variable(
                tf.random_normal([self.hidden_size, self.dict_size]),
            )
            self.ans_fully_b = tf.Variable(tf.zeros([self.dict_size]))

            self.lm_fully_W = tf.Variable(
                tf.random_normal([self.hidden_size, self.dict_size]),
            )
            self.lm_fully_b = tf.Variable(tf.zeros([self.dict_size]))

            # training generation
            lmlot = []  # language model logits over time
            inference_state = state
            inference_output = embedded_in[:, 0, :]

            for time_step in range(self.unroll_len):
                (output, state) = cell(embedded_in[:, time_step, :], state)
                logits = tf.nn.xw_plus_b(
                    output,
                    self.lm_fully_W,
                    self.lm_fully_b,
                )
                lmlot.append(logits)

                mask = self.input_mask[:, time_step]
                mask = tf.expand_dims(mask, -1)
                state_mask = tf.expand_dims(tf.expand_dims(mask, 0), 0)
                inference_state = (
                    state * state_mask + inference_state * (1 - state_mask)
                )
                inference_output = (
                    output * mask + inference_output * (1 - mask)
                )

            self.lm_logits = tf.transpose(
                tf.convert_to_tensor(lmlot),
                [1, 0, 2],
            )

            inference_state = tuple(
                tf.contrib.rnn.LSTMStateTuple(
                    h=inference_state[i, 0],
                    c=inference_state[i, 1],
                )
                for i in range(self.depth)
            )
            output = inference_output
            state = inference_state

            for _ in range(self.unroll_len):
                (output, state) = cell(output, state)
                logits = tf.nn.xw_plus_b(
                    output,
                    self.ans_fully_W,
                    self.ans_fully_b,
                )
                logits_over_time.append(logits)
            logits_over_time = tf.convert_to_tensor(logits_over_time)

            self.ans_logits = tf.transpose(logits_over_time, [1, 0, 2])

            self.ans_result = tf.nn.softmax(self.ans_logits)
            self.lm_result = tf.nn.softmax(self.lm_logits)

            self.lm_loss = tf.reduce_sum(tf.contrib.seq2seq.sequence_loss(
                self.lm_logits[:, :-1, :],
                self.X[:, 1:],
                self.input_mask[:, 1:],
                average_across_timesteps=False,
                average_across_batch=True,
            ))
            self.lm_pred = tf.equal(
                tf.argmax(self.lm_result[:, :-1], axis=-1),
                self.X[:, 1:],
            )
            self.lm_acc = (
                tf.reduce_sum(
                    tf.cast(self.lm_pred, tf.float32) *
                    self.input_mask[:, 1:],
                ) /
                tf.reduce_sum(self.input_mask[:, 1:])
            )

            self.ans_loss = tf.reduce_sum(tf.contrib.seq2seq.sequence_loss(
                self.ans_logits,
                self.Y,
                self.output_mask,
                average_across_timesteps=False,
                average_across_batch=True,
            ))
            self.ans_pred = tf.equal(
                tf.argmax(self.ans_result, axis=-1),
                self.Y,
            )
            self.ans_acc = (
                tf.reduce_sum(
                    tf.cast(self.ans_pred, tf.float32) *
                    self.output_mask,
                ) /
                tf.reduce_sum(self.output_mask)
            )

            optimizer = tf.train.GradientDescentOptimizer(self.learning_rate)
            self.lm_train_op = optimizer.minimize(self.lm_loss)
            self.ans_train_op = optimizer.minimize(self.ans_loss)
