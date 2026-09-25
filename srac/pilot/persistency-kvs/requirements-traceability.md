# Persistency KVS requirements-to-test traceability snapshot

This snapshot is derived from the component requirements and `add_test_properties` metadata at Persistency revision
`9ae529ba9f413976ff5c9948c6490afa51bbfdc3`. It records direct integration-test metadata only. An empty row does not prove that
the requirement is unverified: unit tests, inspections, analyses or other evidence may apply and must be reviewed by the
component expert.

Summary:

- Component requirements: 35
- Requirements with at least one `fully_verifies` reference: 4
- Additional requirements with only `partially_verifies` references: 11
- Requirements with no direct integration-test metadata reference: 20

| Requirement | Title | Fully verified by | Partially verified by | Direct trace status |
|---|---|---|---|---|
| `comp_req__kvs__key_naming` | Key Naming | — | — | No direct metadata trace |
| `comp_req__kvs__key_encoding` | Key Encoding | — | `test_cit_supported_datatypes.TestSupportedDatatypesKeys`<br>`test_cit_supported_datatypes.TestSupportedDatatypesValues` | Partial trace only |
| `comp_req__kvs__key_uniqueness` | Key Uniqueness | — | — | No direct metadata trace |
| `comp_req__kvs__key_length` | Key Length | — | — | No direct metadata trace |
| `comp_req__kvs__value_data_types` | Value Data Types | — | `test_cit_supported_datatypes.TestSupportedDatatypesKeys`<br>`test_cit_supported_datatypes.TestSupportedDatatypesValues` | Partial trace only |
| `comp_req__kvs__value_serialize` | Value Serialization | — | — | No direct metadata trace |
| `comp_req__kvs__value_length` | Value Length | — | — | No direct metadata trace |
| `comp_req__kvs__value_default` | Value Default | — | `test_cit_default_values.TestChecksumOnProvidedDefaults`<br>`test_cit_default_values.TestDefaultValues`<br>`test_cit_default_values.TestMalformedDefaultsFile`<br>`test_cit_default_values.TestMissingDefaultsFile`<br>`test_cit_default_values.TestRemoveKey`<br>`test_cit_default_values.TestResetAllKeys`<br>`test_cit_default_values.TestResetSingleKey` | Partial trace only |
| `comp_req__kvs__value_reset` | Value Reset | `test_cit_default_values.TestResetAllKeys` | — | Full trace present |
| `comp_req__kvs__default_value_types` | Default Value Datatypes | — | `test_cit_default_values.TestDefaultValues`<br>`test_cit_default_values.TestMalformedDefaultsFile`<br>`test_cit_default_values.TestMissingDefaultsFile`<br>`test_cit_default_values.TestRemoveKey`<br>`test_cit_default_values.TestResetAllKeys` | Partial trace only |
| `comp_req__kvs__default_value_query` | Default Value Query | — | `test_cit_default_values.TestDefaultValues` | Partial trace only |
| `comp_req__kvs__default_value_cfg` | Default Value Config | — | `test_cit_default_values.TestChecksumOnProvidedDefaults`<br>`test_cit_default_values.TestDefaultValues`<br>`test_cit_default_values.TestMalformedDefaultsFile`<br>`test_cit_default_values.TestMissingDefaultsFile`<br>`test_cit_default_values.TestRemoveKey`<br>`test_cit_default_values.TestResetAllKeys`<br>`test_cit_default_values.TestResetSingleKey` | Partial trace only |
| `comp_req__kvs__default_val_chksum` | Default Value Checksum | `test_cit_default_values.TestChecksumOnProvidedDefaults` | — | Full trace present |
| `comp_req__kvs__constraints` | Constraint Configuration | — | — | No direct metadata trace |
| `comp_req__kvs__concurrency` | Concurrency | — | `test_cit_multiple_kvs.TestMultipleInstanceIds`<br>`test_cit_multiple_kvs.TestSameInstanceIdDifferentValue`<br>`test_cit_multiple_kvs.TestSameInstanceIdSameValue` | Partial trace only |
| `comp_req__kvs__multi_instance` | Multi-Instance | — | `test_cit_multiple_kvs.TestMultipleInstanceIds`<br>`test_cit_multiple_kvs.TestSameInstanceIdDifferentValue`<br>`test_cit_multiple_kvs.TestSameInstanceIdSameValue` | Partial trace only |
| `comp_req__kvs__persist_data_com` | Persistent Data Storage Components | `test_cit_persistency.TestExplicitFlush` | — | Full trace present |
| `comp_req__kvs__pers_data_csum` | Persistent Data Storage Checksum Write | — | — | No direct metadata trace |
| `comp_req__kvs__pers_data_csum_vrfy` | Persistent Data Storage Checksum Verify | — | — | No direct metadata trace |
| `comp_req__kvs__pers_data_store_bnd` | Persistent Data Storage Backend | — | — | No direct metadata trace |
| `comp_req__kvs__pers_data_store_fmt` | Persistent Data Storage Format | — | — | No direct metadata trace |
| `comp_req__kvs__pers_data_version` | Persistent Data Versioning | — | — | No direct metadata trace |
| `comp_req__kvs__pers_data_schema` | Persistent Data Schema | — | — | No direct metadata trace |
| `comp_req__kvs__snapshot_creation` | Snapshot Creation | — | `test_cit_snapshots.TestSnapshotCountFirstFlush`<br>`test_cit_snapshots.TestSnapshotCountFull`<br>`test_cit_snapshots.TestSnapshotPathsExist`<br>`test_cit_snapshots.TestSnapshotPathsNonexistent`<br>`test_cit_snapshots.TestSnapshotRestoreCurrent`<br>`test_cit_snapshots.TestSnapshotRestoreNonexistent`<br>`test_cit_snapshots.TestSnapshotRestorePrevious` | Partial trace only |
| `comp_req__kvs__snapshot_max_num` | Snapshot Maximum Number | — | `test_cit_snapshots.TestSnapshotMaxCount` | Partial trace only |
| `comp_req__kvs__snapshot_id` | Snapshot IDs | — | — | No direct metadata trace |
| `comp_req__kvs__snapshot_rotate` | Snapshot Rotation | — | `test_cit_snapshots.TestSnapshotRestorePrevious` | Partial trace only |
| `comp_req__kvs__snapshot_restore` | Snapshot Restore | `test_cit_snapshots.TestSnapshotRestorePrevious` | `test_cit_snapshots.TestSnapshotRestoreNonexistent` | Full trace present |
| `comp_req__kvs__snapshot_delete` | Snapshot Deletion | — | — | No direct metadata trace |
| `comp_req__kvs__eng_mode` | Engineering Mode | — | — | No direct metadata trace |
| `comp_req__kvs__field_mode` | Field Mode | — | — | No direct metadata trace |
| `comp_req__kvs__async_api` | Async API | — | — | No direct metadata trace |
| `comp_req__kvs__permission_control` | Permission Control | — | — | No direct metadata trace |
| `comp_req__kvs__permission_err_hndl` | Permission Error Handling | — | — | No direct metadata trace |
| `comp_req__kvs__callback_support` | Callback Support | — | — | No direct metadata trace |

The formal review must determine whether each partial trace is sufficient, whether other verification evidence closes any empty
row, and whether requirements without implementation in the pilot scope should be excluded, deferred or treated as open gaps.
