# AIOS Paper-Trading Signal Queue Draft

Stage: 7.2
Status: Draft planning doc

Defines a queue concept for signals approved only for paper-trading review. Queue fields should include signal_id, strategy_id, queued_at, validation_status, next_action, and checkpoint_file.

Boundary: this queue is not an order queue and must not route broker instructions.
