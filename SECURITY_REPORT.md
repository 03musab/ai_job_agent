# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-27 10:22:50 UTC`  
> **Branch/Ref:** `main` (`e4b66d2d`)  

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
- **File:** [`./app.py:2589`](./app.py#L2589)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
2588         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
2589         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
2590
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:2688`](./app.py#L2688)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
2687                 norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
2688                 job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
2689                 cursor.execute('''
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:3462`](./app.py#L3462)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
3461                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
3462                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
3463                 if new_hash != old_hash:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:4899`](./app.py#L4899)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
4898         norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{self.user_id}"
4899         return hashlib.md5(norm.encode('utf-8')).hexdigest()
4900
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:5653`](./app.py#L5653)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
5652             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
5653             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
5654             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10108`](./app.py#L10108)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10107                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
10108                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
10109                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10638`](./app.py#L10638)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10637                             if contact_data.get('email'):
10638                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
10639                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10642`](./app.py#L10642)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10641                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
10642                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
10643                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 9. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10758`](./app.py#L10758)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10757     if not linkedin_url:
10758         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
10759         linkedin_url = f"manual-entry-{email_hash}"
```

### 10. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:10831`](./app.py#L10831)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
10830                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
10831                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
10832                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 11. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:11436`](./app.py#L11436)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
11435 
11436     cache_key = hashlib.md5(raw_description.encode('utf-8')).hexdigest()
11437     with _JD_FORMAT_CACHE_LOCK:
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2809`](./app.py#L2809)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2808         scope_clause = self._user_scope_clause(cursor, user_id)
2809         query = f"SELECT {query_columns} FROM jobs WHERE {scope_clause}"
2810         params = [user_id]
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2865`](./app.py#L2865)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2864 
2865         count_query = f"SELECT COUNT(*) FROM ({query}) AS filtered_jobs_count"
2866         cursor.execute(count_query, params)
```

### 14. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3056`](./app.py#L3056)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3055             placeholders = ','.join(['?'] * len(job_ids))
3056             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
3057             deleted_count = cursor.rowcount
```

### 15. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3098`](./app.py#L3098)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3097             scope_clause = self._user_scope_clause(cursor, user_id)
3098             cursor.execute(f"SELECT status, COUNT(*) FROM jobs WHERE {scope_clause} AND status IS NOT NULL GROUP BY status", (user_id,))
3099             rows = cursor.fetchall()
```

### 16. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3339`](./app.py#L3339)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3338             scope_clause = self._user_scope_clause(cursor, user_id)
3339             cursor.execute(f"""
3340                 SELECT * FROM jobs WHERE {scope_clause}
3341                 ORDER BY found_date DESC
3342             """, (user_id,))
3343             all_jobs = [dict(r) for r in cursor.fetchall()]
```

### 17. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:4470`](./app.py#L4470)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
4469 
4470         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
4471         cursor.execute(search_query, params)
```

### 18. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:6095`](./app.py#L6095)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
6094                     with open('token.pickle', 'rb') as token:
6095                         creds = pickle.load(token)
6096                     if creds and creds.expired and creds.refresh_token:
```

### 19. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:6649`](./app.py#L6649)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
6648             with open('token.pickle', 'rb') as token:
6649                 creds = pickle.load(token)
6650
```

### 20. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:7705`](./app.py#L7705)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
7704     with open(token_path, 'rb') as token_file:
7705         creds = pickle.load(token_file)
7706
```

### 21. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:8431`](./app.py#L8431)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
8430         return False
8431     return hostname.strip().lower() in ('localhost', '127.0.0.1', '0.0.0.0', '::1')
8432
```

### 22. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:13891`](./app.py#L13891)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
13890     logger.info(f"Starting Flask application on 0.0.0.0:{port} (debug={debug_mode})...")
13891     app.run(debug=debug_mode, host='0.0.0.0', port=port)
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
- **File:** [`./app.py:1483`](./app.py#L1483)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1482                 conn.rollback()
1483             except Exception:
1484                 pass
1485         try:
```

### 36. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1494`](./app.py#L1494)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1493                 conn.rollback()
1494             except Exception:
1495                 pass
1496         cursor.execute("""
```

### 37. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2203`](./app.py#L2203)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2202                 conn.rollback()
2203             except Exception:
2204                 pass
2205             logger.warning(f"Username already exists: {clean_username}")
```

### 38. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2294`](./app.py#L2294)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2293                 conn.rollback()
2294             except Exception:
2295                 pass
2296             return None
```

### 39. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2445`](./app.py#L2445)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2444                 conn.rollback()
2445             except Exception:
2446                 pass
2447             return False, 'That username is already taken. Try one of the suggestions below.'
```

### 40. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2530`](./app.py#L2530)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2529                         conn.rollback()
2530                     except Exception:
2531                         pass
2532             if clean_sub and not (current_sub or '').strip():
```

### 41. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2539`](./app.py#L2539)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2538                         conn.rollback()
2539                     except Exception:
2540                         pass
2541             if clean_avatar and clean_avatar != (current_avatar or '').strip():
```

### 42. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2548`](./app.py#L2548)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2547                         conn.rollback()
2548                     except Exception:
2549                         pass
2550         except Exception as e:
```

### 43. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2735`](./app.py#L2735)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2734                 conn.rollback()
2735             except Exception:
2736                 pass
2737             logger.error(f"Error batch-adding jobs to database: {e}")
```

### 44. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:3738`](./app.py#L3738)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
3737                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
3738                 except Exception:
3739                     continue
3740
```

### 45. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:4336`](./app.py#L4336)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
4335                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
4336                     except Exception:
4337                         pass
4338                 conn.commit()
```

### 46. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:4528`](./app.py#L4528)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
4527                         ))
4528                     except Exception:
4529                         pass
4530                 conn.commit()
```

### 47. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4678`](./app.py#L4678)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4677             options.add_argument('--disable-dev-shm-usage')
4678             random_user_agent = random.choice(USER_AGENTS)
4679             options.add_argument(f"user-agent={random_user_agent}")
```

### 48. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4970`](./app.py#L4970)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4969             }
4970             headers = {'User-Agent': random.choice(USER_AGENTS)}
4971             try:
```

### 49. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4973`](./app.py#L4973)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4972                 if page > 0:
4973                     time.sleep(random.uniform(*self.request_delay))
4974                 response = session.get(base_url, params=params, headers=headers, timeout=self.http_timeout)
```

### 50. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5072`](./app.py#L5072)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5071                 )
5072                 detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
5073                 time.sleep(random.uniform(*self.linkedin_detail_delay))
```

### 51. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5073`](./app.py#L5073)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5072                 detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
5073                 time.sleep(random.uniform(*self.linkedin_detail_delay))
5074                 resp = self._get_http_session().get(detail_url, headers=detail_headers, timeout=self.http_timeout)
```

### 52. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5155`](./app.py#L5155)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5154                 headers = {
5155                     'User-Agent': random.choice(USER_AGENTS),
5156                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 53. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5160`](./app.py#L5160)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5159                 if page > 1:
5160                     time.sleep(random.uniform(*self.request_delay))
5161
```

### 54. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5374`](./app.py#L5374)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5373             logger.debug(f"[Internshala] Fetching details: {link}")
5374             time.sleep(random.uniform(*self.internshala_detail_delay))
5375
```

### 55. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:5377`](./app.py#L5377)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
5376             headers = {
5377                 'User-Agent': random.choice(USER_AGENTS),
5378                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 56. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:6749`](./app.py#L6749)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
6748                                 row[rel_col-1].value = f"🔴 {val}"
6749                         except:
6750                             continue
6751                 # --- Make Links Clickable and Button Style ---
```

### 57. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:7318`](./app.py#L7318)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
7317                             os.remove(excel_file)
7318                         except Exception:
7319                             pass
7320
```

### 58. [ℹ️ LOW] Possible hardcoded password: 'token.pickle'
- **File:** [`./app.py:7700`](./app.py#L7700)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
7699     """Send a MIME message via existing non-interactive Gmail OAuth credentials."""
7700     token_path = 'token.pickle'
7701     if not os.path.exists(token_path):
```

### 59. [ℹ️ LOW] Possible hardcoded password: 'https://oauth2.googleapis.com/token'
- **File:** [`./app.py:8466`](./app.py#L8466)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
8465             'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
8466             'token_uri': 'https://oauth2.googleapis.com/token',
8467             'redirect_uris': [callback_uri],
8468         }
8469     }
8470     os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')
8471     # Request only non-sensitive identity scopes on standard sign-in so Google displays
8472     # verified branding without the "Google hasn't verified this app" sensitive-scope warning.
8473     include_sensitive = os.environ.get('GOOGLE_OAUTH_INCLUDE_SENSITIVE_SCOPES', '0').lower() in ('1', 'true', 'yes')
```

### 60. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:9532`](./app.py#L9532)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
9531             return {'current_user_avatar_url': avatar_url}
9532     except Exception:
9533         pass
9534     return {'current_user_avatar_url': ''}
```

### 61. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:9679`](./app.py#L9679)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
9678                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
9679             except Exception:
9680                 pass
9681
```

### 62. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:10258`](./app.py#L10258)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
10257             stored_remind_iso = dt_utc.isoformat()
10258         except Exception:
10259             pass
10260
```

### 63. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:11884`](./app.py#L11884)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
11883     fake_analysis_data = {
11884         "monthly_visits": f"{random.randint(50, 500)}K",
11885         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 64. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:11885`](./app.py#L11885)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
11884         "monthly_visits": f"{random.randint(50, 500)}K",
11885         "bounce_rate": f"{random.randint(30, 70)}%",
11886         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 65. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:11886`](./app.py#L11886)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
11885         "bounce_rate": f"{random.randint(30, 70)}%",
11886         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
11887     }
```

### 66. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:12393`](./app.py#L12393)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
12392                 db.release_scrape_slot_on_failure(current_user.id)
12393             except Exception:
12394                 pass
12395         logger.error(f"Failed to start scraping task: {e}")
```

### 67. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:12640`](./app.py#L12640)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
12639                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
12640             except Exception:
12641                 pass
12642             return jsonify({
```

### 68. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:13744`](./app.py#L13744)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
13743                 user_name = user_details.get('full_name')
13744         except Exception:
13745             pass
13746
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
