Probably:

- add name of instance snapshotted volume was attached to at time of snapshot run to Description
  - Add during snapshot instance name tracking to snapshot creator
- add device name on instance snapshotted volume was attached to at time of snapshot run to Description
  - Add during snapshot instance volume device name tracking to snapshot creator
- Investigate failure scenarios for snapshot creator
- Investigate how to improve notification/alerting on failure for snapshot creator
- Add support for out-of-region snapshots

Maybe:

- Add support for retention of most recent X weeks to manager (versus current only most recent X days support)
- Add support for retention of most recent X months to manager (versus current only most recent X days support)
