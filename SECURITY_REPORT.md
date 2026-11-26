# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-26 10:16:37 UTC`  
> **Branch/Ref:** `main` (`3b4c654f`)  

## 📊 Executive Summary

| Category | Findings | Severity Note |
| :--- | :--- | :--- |
| **🚨 High Severity (Code)** | `11` | Critical flaws, injection, or hardcoded secrets |
| **⚠️ Medium Severity (Code)** | `18` | Weak crypto, insecure configs, or unvalidated parameters |
| **ℹ️ Low Severity (Code)** | `82` | Information leaks or minor code hygiene warnings |
| **📦 Known CVEs (Dependencies)** | `0` | Vulnerabilities identified in third-party packages |
| **Total Security Items** | `111` | Combined code & dependency signals |

## 🔍 Code Security Vulnerabilities (SAST)

Identified `111` code security items across Python source files:

### 1. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:2535`](./app.py#L2535)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
2534         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
2535         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
2536
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:2634`](./app.py#L2634)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
2633                 norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
2634                 job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
2635                 cursor.execute('''
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:3408`](./app.py#L3408)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
3407                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
3408                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
3409                 if new_hash != old_hash:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:4845`](./app.py#L4845)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
4844         norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{self.user_id}"
4845         return hashlib.md5(norm.encode('utf-8')).hexdigest()
4846
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:5599`](./app.py#L5599)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
5598             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
5599             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
5600             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10054`](./app.py#L10054)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10053                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
10054                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
10055                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10584`](./app.py#L10584)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10583                             if contact_data.get('email'):
10584                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
10585                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10588`](./app.py#L10588)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10587                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
10588                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
10589                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 9. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10704`](./app.py#L10704)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10703     if not linkedin_url:
10704         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
10705         linkedin_url = f"manual-entry-{email_hash}"
```

### 10. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10777`](./app.py#L10777)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10776                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
10777                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
10778                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 11. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:11382`](./app.py#L11382)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
11381 
11382     cache_key = hashlib.md5(raw_description.encode('utf-8')).hexdigest()
11383     with _JD_FORMAT_CACHE_LOCK:
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2755`](./app.py#L2755)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2754         scope_clause = self._user_scope_clause(cursor, user_id)
2755         query = f"SELECT {query_columns} FROM jobs WHERE {scope_clause}"
2756         params = [user_id]
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2811`](./app.py#L2811)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2810 
2811         count_query = f"SELECT COUNT(*) FROM ({query}) AS filtered_jobs_count"
2812         cursor.execute(count_query, params)
```

### 14. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3002`](./app.py#L3002)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3001             placeholders = ','.join(['?'] * len(job_ids))
3002             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
3003             deleted_count = cursor.rowcount
```

### 15. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3044`](./app.py#L3044)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3043             scope_clause = self._user_scope_clause(cursor, user_id)
3044             cursor.execute(f"SELECT status, COUNT(*) FROM jobs WHERE {scope_clause} AND status IS NOT NULL GROUP BY status", (user_id,))
3045             rows = cursor.fetchall()
```

### 16. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3285`](./app.py#L3285)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3284             scope_clause = self._user_scope_clause(cursor, user_id)
3285             cursor.execute(f"""
3286                 SELECT * FROM jobs WHERE {scope_clause}
3287                 ORDER BY found_date DESC
3288             """, (user_id,))
3289             all_jobs = [dict(r) for r in cursor.fetchall()]
```

### 17. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:4416`](./app.py#L4416)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
4415 
4416         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
4417         cursor.execute(search_query, params)
```

### 18. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:6041`](./app.py#L6041)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
6040                     with open('token.pickle', 'rb') as token:
6041                         creds = pickle.load(token)
6042                     if creds and creds.expired and creds.refresh_token:
```

### 19. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:6595`](./app.py#L6595)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
6594             with open('token.pickle', 'rb') as token:
6595                 creds = pickle.load(token)
6596
```

### 20. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:7651`](./app.py#L7651)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
7650     with open(token_path, 'rb') as token_file:
7651         creds = pickle.load(token_file)
7652
```

### 21. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:8377`](./app.py#L8377)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
8376         return False
8377     return hostname.strip().lower() in ('localhost', '127.0.0.1', '0.0.0.0', '::1')
8378
```

### 22. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:13837`](./app.py#L13837)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
13836     logger.info(f"Starting Flask application on 0.0.0.0:{port} (debug={debug_mode})...")
13837     app.run(debug=debug_mode, host='0.0.0.0', port=port)
```

### 23. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./database.py:71`](./database.py#L71)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
70         return (
71             "SELECT ordinal_position - 1 AS cid, column_name AS name "
72             "FROM information_schema.columns "
73             "WHERE table_schema = current_schema() AND table_name = "
74             f"'{table_name}' ORDER BY ordinal_position"
75         )
```

### 24. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./scripts/migrate_sqlite_to_postgres.py:116`](./scripts/migrate_sqlite_to_postgres.py#L116)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
115     )
116     source_cursor = source.execute(f'SELECT * FROM "{table}"')
117     copied = 0
```

### 25. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./scripts/proc_runner.py:120`](./scripts/proc_runner.py#L120)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
119     debug = _is_truthy(os.environ.get("FLASK_DEBUG") or os.environ.get("DEBUG"))
120     app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
121     return 0
```

### 26. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./scripts/reset_all_data.py:136`](./scripts/reset_all_data.py#L136)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
135             try:
136                 cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
137                 counts[tbl] = cur.fetchone()[0]
```

### 27. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./scripts/reset_all_data.py:258`](./scripts/reset_all_data.py#L258)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
257             for tbl in target_existing:
258                 cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
259                 cnt = cur.fetchone()[0]
```

### 28. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./scripts/reset_all_data.py:277`](./scripts/reset_all_data.py#L277)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
276             for tbl in target_existing:
277                 cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
278                 cnt = cur.fetchone()[0]
```

### 29. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./send_launch_emails.py:263`](./send_launch_emails.py#L263)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
262     with open(token_path, "rb") as token:
263         creds = pickle.load(token)
264
```

### 30. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:112`](./ai_utils.py#L112)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
111         return json.loads(text)
112     except Exception:
113         pass
114
```

### 31. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./ai_utils.py:126`](./ai_utils.py#L126)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
125             return json.loads(cand)
126         except Exception:
127             continue
128
```

### 32. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:136`](./ai_utils.py#L136)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
135             return json.loads(sub)
136         except Exception:
137             pass
138
```

### 33. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:146`](./ai_utils.py#L146)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
145             return json.loads(sub)
146         except Exception:
147             pass
148
```

### 34. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./app.py:13`](./app.py#L13)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
12 import os
13 import pickle
14 import random
```

### 35. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1429`](./app.py#L1429)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1428                 conn.rollback()
1429             except Exception:
1430                 pass
1431         try:
```

### 36. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1440`](./app.py#L1440)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1439                 conn.rollback()
1440             except Exception:
1441                 pass
1442         cursor.execute("""
```

### 37. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2149`](./app.py#L2149)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2148                 conn.rollback()
2149             except Exception:
2150                 pass
2151             logger.warning(f"Username already exists: {clean_username}")
```

### 38. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2240`](./app.py#L2240)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2239                 conn.rollback()
2240             except Exception:
2241                 pass
2242             return None
```

### 39. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2391`](./app.py#L2391)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2390                 conn.rollback()
2391             except Exception:
2392                 pass
2393             return False, 'That username is already taken. Try one of the suggestions below.'
```

### 40. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2476`](./app.py#L2476)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2475                         conn.rollback()
2476                     except Exception:
2477                         pass
2478             if clean_sub and not (current_sub or '').strip():
```

### 41. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2485`](./app.py#L2485)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2484                         conn.rollback()
2485                     except Exception:
2486                         pass
2487             if clean_avatar and clean_avatar != (current_avatar or '').strip():
```

### 42. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2494`](./app.py#L2494)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2493                         conn.rollback()
2494                     except Exception:
2495                         pass
2496         except Exception as e:
```

### 43. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2681`](./app.py#L2681)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2680                 conn.rollback()
2681             except Exception:
2682                 pass
2683             logger.error(f"Error batch-adding jobs to database: {e}")
```

### 44. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:3684`](./app.py#L3684)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
3683                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
3684                 except Exception:
3685                     continue
3686
```

### 45. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:4282`](./app.py#L4282)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
4281                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
4282                     except Exception:
4283                         pass
4284                 conn.commit()
```

### 46. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:4474`](./app.py#L4474)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
4473                         ))
4474                     except Exception:
4475                         pass
4476                 conn.commit()
```

### 47. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4624`](./app.py#L4624)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4623             options.add_argument('--disable-dev-shm-usage')
4624             random_user_agent = random.choice(USER_AGENTS)
4625             options.add_argument(f"user-agent={random_user_agent}")
```

### 48. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4916`](./app.py#L4916)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4915             }
4916             headers = {'User-Agent': random.choice(USER_AGENTS)}
4917             try:
```

### 49. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4919`](./app.py#L4919)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4918                 if page > 0:
4919                     time.sleep(random.uniform(*self.request_delay))
4920                 response = session.get(base_url, params=params, headers=headers, timeout=self.http_timeout)
```

### 50. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5018`](./app.py#L5018)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5017                 )
5018                 detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
5019                 time.sleep(random.uniform(*self.linkedin_detail_delay))
```

### 51. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5019`](./app.py#L5019)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5018                 detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
5019                 time.sleep(random.uniform(*self.linkedin_detail_delay))
5020                 resp = self._get_http_session().get(detail_url, headers=detail_headers, timeout=self.http_timeout)
```

### 52. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5101`](./app.py#L5101)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5100                 headers = {
5101                     'User-Agent': random.choice(USER_AGENTS),
5102                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 53. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5106`](./app.py#L5106)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5105                 if page > 1:
5106                     time.sleep(random.uniform(*self.request_delay))
5107
```

### 54. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5320`](./app.py#L5320)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5319             logger.debug(f"[Internshala] Fetching details: {link}")
5320             time.sleep(random.uniform(*self.internshala_detail_delay))
5321
```

### 55. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5323`](./app.py#L5323)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5322             headers = {
5323                 'User-Agent': random.choice(USER_AGENTS),
5324                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 56. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:6695`](./app.py#L6695)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
6694                                 row[rel_col-1].value = f"🔴 {val}"
6695                         except:
6696                             continue
6697                 # --- Make Links Clickable and Button Style ---
```

### 57. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:7264`](./app.py#L7264)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
7263                             os.remove(excel_file)
7264                         except Exception:
7265                             pass
7266
```

### 58. [ℹ️ LOW] Possible hardcoded password: 'token.pickle'
- **File:** [`./app.py:7646`](./app.py#L7646)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
7645     """Send a MIME message via existing non-interactive Gmail OAuth credentials."""
7646     token_path = 'token.pickle'
7647     if not os.path.exists(token_path):
```

### 59. [ℹ️ LOW] Possible hardcoded password: 'https://oauth2.googleapis.com/token'
- **File:** [`./app.py:8412`](./app.py#L8412)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
8411             'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
8412             'token_uri': 'https://oauth2.googleapis.com/token',
8413             'redirect_uris': [callback_uri],
8414         }
8415     }
8416     os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')
8417     # Request only non-sensitive identity scopes on standard sign-in so Google displays
8418     # verified branding without the "Google hasn't verified this app" sensitive-scope warning.
8419     include_sensitive = os.environ.get('GOOGLE_OAUTH_INCLUDE_SENSITIVE_SCOPES', '0').lower() in ('1', 'true', 'yes')
```

### 60. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:9478`](./app.py#L9478)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
9477             return {'current_user_avatar_url': avatar_url}
9478     except Exception:
9479         pass
9480     return {'current_user_avatar_url': ''}
```

### 61. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:9625`](./app.py#L9625)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
9624                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
9625             except Exception:
9626                 pass
9627
```

### 62. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:10204`](./app.py#L10204)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
10203             stored_remind_iso = dt_utc.isoformat()
10204         except Exception:
10205             pass
10206
```

### 63. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:11830`](./app.py#L11830)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
11829     fake_analysis_data = {
11830         "monthly_visits": f"{random.randint(50, 500)}K",
11831         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 64. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:11831`](./app.py#L11831)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
11830         "monthly_visits": f"{random.randint(50, 500)}K",
11831         "bounce_rate": f"{random.randint(30, 70)}%",
11832         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 65. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:11832`](./app.py#L11832)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
11831         "bounce_rate": f"{random.randint(30, 70)}%",
11832         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
11833     }
```

### 66. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:12339`](./app.py#L12339)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
12338                 db.release_scrape_slot_on_failure(current_user.id)
12339             except Exception:
12340                 pass
12341         logger.error(f"Failed to start scraping task: {e}")
```

### 67. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:12586`](./app.py#L12586)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
12585                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
12586             except Exception:
12587                 pass
12588             return jsonify({
```

### 68. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:13690`](./app.py#L13690)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
13689                 user_name = user_details.get('full_name')
13690         except Exception:
13691             pass
13692
```

### 69. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./jobsnap-luminous-video/make_final.py:18`](./jobsnap-luminous-video/make_final.py#L18)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
17 """
18 import pathlib, shutil, subprocess, sys, wave
19 import numpy as np
```

### 70. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/make_final.py:45`](./jobsnap-luminous-video/make_final.py#L45)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
44     tmp.parent.mkdir(parents=True, exist_ok=True)
45     subprocess.run(
46         ["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", str(tmp)],
47         check=True,
48     )
49     with wave.open(str(tmp), "rb") as wf:
```

### 71. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/make_final.py:45`](./jobsnap-luminous-video/make_final.py#L45)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
44     tmp.parent.mkdir(parents=True, exist_ok=True)
45     subprocess.run(
46         ["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", str(tmp)],
47         check=True,
48     )
49     with wave.open(str(tmp), "rb") as wf:
```

### 72. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/make_final.py:217`](./jobsnap-luminous-video/make_final.py#L217)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
216     print("  Rendering fresh 1080p video frames via HyperFrames...")
217     subprocess.run([sys.executable, str(ROOT / "src" / "build.py")], cwd=ROOT, check=True)
218     npx_bin = shutil.which("npx.cmd") or shutil.which("npx") or "npx.cmd"
```

### 73. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/make_final.py:219`](./jobsnap-luminous-video/make_final.py#L219)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
218     npx_bin = shutil.which("npx.cmd") or shutil.which("npx") or "npx.cmd"
219     subprocess.run([npx_bin, "--yes", "hyperframes", "render", "-q", "high", "-o", str(video_cache)], cwd=ROOT, check=True)
220 elif found_vid != video_cache:
```

### 74. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/make_final.py:221`](./jobsnap-luminous-video/make_final.py#L221)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
220 elif found_vid != video_cache:
221     subprocess.run(
222         ["ffmpeg", "-v", "error", "-y", "-i", str(found_vid), "-an", "-c:v", "copy", str(video_cache)],
223         check=True,
224     )
225
```

### 75. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/make_final.py:221`](./jobsnap-luminous-video/make_final.py#L221)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
220 elif found_vid != video_cache:
221     subprocess.run(
222         ["ffmpeg", "-v", "error", "-y", "-i", str(found_vid), "-an", "-c:v", "copy", str(video_cache)],
223         check=True,
224     )
225
```

### 76. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/make_final.py:333`](./jobsnap-luminous-video/make_final.py#L333)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
332 
333 subprocess.run(
334     [
335         "ffmpeg", "-v", "error", "-y",
336         "-i", str(video_cache),
337         "-i", str(master_wav),
338         "-map", "0:v:0",
339         "-map", "1:a:0",
340         "-c:v", "copy",
341         "-c:a", "aac", "-b:a", "256k",
342         "-t", str(DUR),
343         "-movflags", "+faststart",
344         str(out_mp4),
345     ],
346     check=True,
347 )
348
```

### 77. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/make_final.py:333`](./jobsnap-luminous-video/make_final.py#L333)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
332 
333 subprocess.run(
334     [
335         "ffmpeg", "-v", "error", "-y",
336         "-i", str(video_cache),
337         "-i", str(master_wav),
338         "-map", "0:v:0",
339         "-map", "1:a:0",
340         "-c:v", "copy",
341         "-c:a", "aac", "-b:a", "256k",
342         "-t", str(DUR),
343         "-movflags", "+faststart",
344         str(out_mp4),
345     ],
346     check=True,
347 )
348
```

### 78. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/make_final.py:349`](./jobsnap-luminous-video/make_final.py#L349)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
348 
349 subprocess.run(
350     [
351         "ffmpeg", "-v", "error", "-y",
352         "-i", str(out_mp4),
353         "-c:v", "libx264", "-b:v", "4500k", "-maxrate", "6000k", "-bufsize", "12000k",
354         "-preset", "fast", "-pix_fmt", "yuv420p",
355         "-c:a", "aac", "-b:a", "192k",
356         "-movflags", "+faststart",
357         str(out_social),
358     ],
359     check=True,
360 )
361
```

### 79. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/make_final.py:349`](./jobsnap-luminous-video/make_final.py#L349)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
348 
349 subprocess.run(
350     [
351         "ffmpeg", "-v", "error", "-y",
352         "-i", str(out_mp4),
353         "-c:v", "libx264", "-b:v", "4500k", "-maxrate", "6000k", "-bufsize", "12000k",
354         "-preset", "fast", "-pix_fmt", "yuv420p",
355         "-c:a", "aac", "-b:a", "192k",
356         "-movflags", "+faststart",
357         str(out_social),
358     ],
359     check=True,
360 )
361
```

### 80. [ℹ️ LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **File:** [`./jobsnap-luminous-video/src/build.py:19`](./jobsnap-luminous-video/src/build.py#L19)
- **Rule ID:** `B101` (assert_used)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b101_assert_used.html)

```python
18 scenes = "\n".join(f.read_text(encoding="utf-8") for f in sorted((root / "src" / "scenes").glob("*.js")))
19 assert "/*__DATA__*/" in src and "/*__SCENES__*/" in src
20 src = src.replace("/*__DATA__*/", data).replace("/*__SCENES__*/", scenes)
```

### 81. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./jobsnap-luminous-video/src/clone_voice.py:15`](./jobsnap-luminous-video/src/clone_voice.py#L15)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
14 """
15 import argparse, os, pathlib, subprocess, sys, urllib.request, json
16
```

### 82. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/src/clone_voice.py:80`](./jobsnap-luminous-video/src/clone_voice.py#L80)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
79     clean_ref = ROOT / "work" / "ref_clean.wav"
80     subprocess.run(
81         ["ffmpeg", "-v", "error", "-y", "-i", str(SAMPLE), "-ss", "5", "-t", "12", "-ac", "1", "-ar", "24000", str(clean_ref)],
82         check=True,
83     )
84     print("Running local F5-TTS voice cloning (first run downloads model weights)...")
```

### 83. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/src/clone_voice.py:80`](./jobsnap-luminous-video/src/clone_voice.py#L80)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
79     clean_ref = ROOT / "work" / "ref_clean.wav"
80     subprocess.run(
81         ["ffmpeg", "-v", "error", "-y", "-i", str(SAMPLE), "-ss", "5", "-t", "12", "-ac", "1", "-ar", "24000", str(clean_ref)],
82         check=True,
83     )
84     print("Running local F5-TTS voice cloning (first run downloads model weights)...")
```

### 84. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/src/clone_voice.py:85`](./jobsnap-luminous-video/src/clone_voice.py#L85)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
84     print("Running local F5-TTS voice cloning (first run downloads model weights)...")
85     subprocess.run(
86         [
87             "f5-tts_infer-cli",
88             "--model", "F5TTS_v1_Base",
89             "--ref_audio", str(clean_ref),
90             "--gen_text", SCRIPT,
91             "--output_dir", str(out_dir),
92             "--output_file", "vo_cloned.wav",
93         ],
94         check=True,
95     )
96     final_wav = ROOT / "work" / "vo_cloned.wav"
```

### 85. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/src/clone_voice.py:85`](./jobsnap-luminous-video/src/clone_voice.py#L85)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
84     print("Running local F5-TTS voice cloning (first run downloads model weights)...")
85     subprocess.run(
86         [
87             "f5-tts_infer-cli",
88             "--model", "F5TTS_v1_Base",
89             "--ref_audio", str(clean_ref),
90             "--gen_text", SCRIPT,
91             "--output_dir", str(out_dir),
92             "--output_file", "vo_cloned.wav",
93         ],
94         check=True,
95     )
96     final_wav = ROOT / "work" / "vo_cloned.wav"
```

### 86. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./jobsnap-luminous-video/src/mix_sfx.py:15`](./jobsnap-luminous-video/src/mix_sfx.py#L15)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
14 """
15 import pathlib, subprocess
16 import numpy as np
```

### 87. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/src/mix_sfx.py:250`](./jobsnap-luminous-video/src/mix_sfx.py#L250)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
249 out = ROOT / "assets" / "audio" / "sfx.wav"
250 subprocess.run(
251     ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(out)],
252     input=bus.astype(np.float32).tobytes(),
253     check=True,
254 )
255 print(f"wrote {out.relative_to(ROOT)} (32.0s, 36 punchy stereo SFX cues, peak {20*np.log10(float(np.max(np.abs(bus)))+1e-9):.1f} dBFS)")
```

### 88. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/src/mix_sfx.py:250`](./jobsnap-luminous-video/src/mix_sfx.py#L250)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
249 out = ROOT / "assets" / "audio" / "sfx.wav"
250 subprocess.run(
251     ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(out)],
252     input=bus.astype(np.float32).tobytes(),
253     check=True,
254 )
255 print(f"wrote {out.relative_to(ROOT)} (32.0s, 36 punchy stereo SFX cues, peak {20*np.log10(float(np.max(np.abs(bus)))+1e-9):.1f} dBFS)")
```

### 89. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./jobsnap-luminous-video/src/music.py:9`](./jobsnap-luminous-video/src/music.py#L9)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
8 """
9 import json, pathlib, subprocess, sys
10 import numpy as np
```

### 90. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/src/music.py:30`](./jobsnap-luminous-video/src/music.py#L30)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
29 
30 raw = subprocess.run(
31     ["ffmpeg", "-v", "error", "-i", str(SRC), "-af", "loudnorm=I=-15:TP=-1.5:LRA=9", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
32     capture_output=True,
33     check=True,
34 ).stdout
35 x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
```

### 91. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/src/music.py:30`](./jobsnap-luminous-video/src/music.py#L30)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
29 
30 raw = subprocess.run(
31     ["ffmpeg", "-v", "error", "-i", str(SRC), "-af", "loudnorm=I=-15:TP=-1.5:LRA=9", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
32     capture_output=True,
33     check=True,
34 ).stdout
35 x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
```

### 92. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/src/music.py:58`](./jobsnap-luminous-video/src/music.py#L58)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
57 out = ROOT / "assets" / "audio" / "music.wav"
58 subprocess.run(
59     ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(out)],
60     input=(y * g).tobytes(),
61     check=True,
62 )
63 print(f"wrote {out.relative_to(ROOT)} from {SRC.name} ({DUR}s, bed={BED}, outro={OUTRO_GAIN})")
```

### 93. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/src/music.py:58`](./jobsnap-luminous-video/src/music.py#L58)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
57 out = ROOT / "assets" / "audio" / "music.wav"
58 subprocess.run(
59     ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(out)],
60     input=(y * g).tobytes(),
61     check=True,
62 )
63 print(f"wrote {out.relative_to(ROOT)} from {SRC.name} ({DUR}s, bed={BED}, outro={OUTRO_GAIN})")
```

### 94. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./jobsnap-luminous-video/src/voice.py:10`](./jobsnap-luminous-video/src/voice.py#L10)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
9 """
10 import json, pathlib, subprocess, difflib, re, sys, shutil
11 import numpy as np
```

### 95. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/src/voice.py:25`](./jobsnap-luminous-video/src/voice.py#L25)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
24 def dec(path, extra=()):
25     raw = subprocess.run(
26         ["ffmpeg", "-v", "error", "-i", str(path), *extra, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
27         capture_output=True,
28         check=True,
29     ).stdout
30     return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
```

### 96. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/src/voice.py:25`](./jobsnap-luminous-video/src/voice.py#L25)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
24 def dec(path, extra=()):
25     raw = subprocess.run(
26         ["ffmpeg", "-v", "error", "-i", str(path), *extra, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
27         capture_output=True,
28         check=True,
29     ).stdout
30     return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
```

### 97. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./jobsnap-luminous-video/src/voice.py:75`](./jobsnap-luminous-video/src/voice.py#L75)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
74 vo = ROOT / "assets" / "audio" / "vo.wav"
75 subprocess.run(
76     ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", f"atempo={SPEED},alimiter=limit=0.84", "-c:a", "pcm_s24le", str(vo)],
77     input=out.tobytes(),
78     check=True,
79 )
80 dur_s = len(out) / SR / SPEED
```

### 98. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./jobsnap-luminous-video/src/voice.py:75`](./jobsnap-luminous-video/src/voice.py#L75)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
74 vo = ROOT / "assets" / "audio" / "vo.wav"
75 subprocess.run(
76     ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", f"atempo={SPEED},alimiter=limit=0.84", "-c:a", "pcm_s24le", str(vo)],
77     input=out.tobytes(),
78     check=True,
79 )
80 dur_s = len(out) / SR / SPEED
```

### 99. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:48`](./outreach_scraper.py#L48)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
47         self.session = requests.Session()
48         self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
49         self.scraped_domains = set()
```

### 100. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:108`](./outreach_scraper.py#L108)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
107         # Add random delay to appear more human
108         time.sleep(random.uniform(self.min_delay, self.max_delay))
109
```

### 101. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./scripts/proc_runner.py:14`](./scripts/proc_runner.py#L14)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
13 import os
14 import subprocess
15 import sys
```

### 102. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:293`](./scripts/proc_runner.py#L293)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
292             sys.stderr.flush()
293         except Exception:
294             pass
295         if job_handle:
```

### 103. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./scripts/proc_runner.py:299`](./scripts/proc_runner.py#L299)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
298             try:
299                 subprocess.run(
300                     ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
301                     stdout=subprocess.DEVNULL,
302                     stderr=subprocess.DEVNULL,
303                     timeout=3,
304                     check=False,
305                 )
306             except Exception:
```

### 104. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./scripts/proc_runner.py:299`](./scripts/proc_runner.py#L299)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
298             try:
299                 subprocess.run(
300                     ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
301                     stdout=subprocess.DEVNULL,
302                     stderr=subprocess.DEVNULL,
303                     timeout=3,
304                     check=False,
305                 )
306             except Exception:
```

### 105. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:306`](./scripts/proc_runner.py#L306)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
305                 )
306             except Exception:
307                 pass
308             try:
```

### 106. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:310`](./scripts/proc_runner.py#L310)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
309                 proc.kill()
310             except Exception:
311                 pass
312         os._exit(0)
```

### 107. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./scripts/proc_runner.py:332`](./scripts/proc_runner.py#L332)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
331 
332         proc = subprocess.Popen(cmd, env=env, cwd=str(REPO_ROOT))
333         if child_job is not None:
```

### 108. [ℹ️ LOW] Starting a process without a shell.
- **File:** [`./scripts/proc_runner.py:398`](./scripts/proc_runner.py#L398)
- **Rule ID:** `B606` (start_process_with_no_shell)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b606_start_process_with_no_shell.html)

```python
397         os.chdir(REPO_ROOT)
398         os.execvpe(cmd[0], cmd, env)
399
```

### 109. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/reset_all_data.py:39`](./scripts/reset_all_data.py#L39)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
38     load_dotenv(ROOT_DIR / ".env")
39 except Exception:
40     pass
41
```

### 110. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./send_launch_emails.py:13`](./send_launch_emails.py#L13)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
12 import base64
13 import pickle
14 import argparse
```

### 111. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./send_launch_emails.py:361`](./send_launch_emails.py#L361)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
360         raw_role = (c.get("Role_Category") or "").strip() or "your field"
361         ticket_id = c.get("TicketId") or c.get("PassCode") or f"JS-{random.randint(1000, 9999)}"
362         subject = tmpl["subject"].format(name=raw_name, role=raw_role)
```

## 📦 Dependency Vulnerability Scan (CVEs)

✅ **No vulnerable third-party dependencies detected.** All scanned packages comply with published security advisories.
## 🛠️ Security Remediation Guidance

- [ ] **Rotate / Environment Variables**: Ensure all database URLs, API tokens, and JWT secrets are injected via `.env` or GitHub Secrets, never hardcoded in source.
- [ ] **Parameterized Queries**: Verify that SQL queries in `app.py` use SQLAlchemy ORM or bound parameters (`db.session.execute(text(...), {'param': val})`).
- [ ] **Dependency Patching**: Run `pip install --upgrade <package>` to bump flagged libraries to their recommended patch versions.
- [ ] **CSRF & Session Hardening**: Ensure `WTF_CSRF_ENABLED=True` and secure cookie flags (`SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`) are active.

---
*This report is automatically generated and updated on each push and scheduled audit by the AI JobSnap Security Agent workflow.*
