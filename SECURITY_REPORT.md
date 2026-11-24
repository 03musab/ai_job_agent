# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-24 11:52:41 UTC`  
> **Branch/Ref:** `main` (`aa1865e1`)  

## 📊 Executive Summary

| Category | Findings | Severity Note |
| :--- | :--- | :--- |
| **🚨 High Severity (Code)** | `11` | Critical flaws, injection, or hardcoded secrets |
| **⚠️ Medium Severity (Code)** | `15` | Weak crypto, insecure configs, or unvalidated parameters |
| **ℹ️ Low Severity (Code)** | `47` | Information leaks or minor code hygiene warnings |
| **📦 Known CVEs (Dependencies)** | `0` | Vulnerabilities identified in third-party packages |
| **Total Security Items** | `73` | Combined code & dependency signals |

## 🔍 Code Security Vulnerabilities (SAST)

Identified `73` code security items across Python source files:

### 1. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1709`](./app.py#L1709)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1708         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
1709         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1710
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1808`](./app.py#L1808)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1807                 norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
1808                 job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1809                 cursor.execute('''
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:2580`](./app.py#L2580)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
2579                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
2580                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
2581                 if new_hash != old_hash:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:3976`](./app.py#L3976)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
3975         norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{self.user_id}"
3976         return hashlib.md5(norm.encode('utf-8')).hexdigest()
3977
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:4730`](./app.py#L4730)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
4729             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
4730             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
4731             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:8888`](./app.py#L8888)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
8887                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
8888                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
8889                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:9185`](./app.py#L9185)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
9184                             if contact_data.get('email'):
9185                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
9186                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:9189`](./app.py#L9189)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
9188                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
9189                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
9190                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 9. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:9305`](./app.py#L9305)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
9304     if not linkedin_url:
9305         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
9306         linkedin_url = f"manual-entry-{email_hash}"
```

### 10. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:9378`](./app.py#L9378)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
9377                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
9378                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
9379                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 11. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:9993`](./app.py#L9993)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
9992 
9993     cache_key = hashlib.md5(raw_description.encode('utf-8')).hexdigest()
9994     with _JD_FORMAT_CACHE_LOCK:
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1929`](./app.py#L1929)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1928         scope_clause = self._user_scope_clause(cursor, user_id)
1929         query = f"SELECT {query_columns} FROM jobs WHERE {scope_clause}"
1930         params = [user_id]
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1985`](./app.py#L1985)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1984 
1985         count_query = f"SELECT COUNT(*) FROM ({query}) AS filtered_jobs_count"
1986         cursor.execute(count_query, params)
```

### 14. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2174`](./app.py#L2174)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2173             placeholders = ','.join(['?'] * len(job_ids))
2174             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
2175             deleted_count = cursor.rowcount
```

### 15. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2216`](./app.py#L2216)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2215             scope_clause = self._user_scope_clause(cursor, user_id)
2216             cursor.execute(f"SELECT status, COUNT(*) FROM jobs WHERE {scope_clause} AND status IS NOT NULL GROUP BY status", (user_id,))
2217             rows = cursor.fetchall()
```

### 16. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2457`](./app.py#L2457)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2456             scope_clause = self._user_scope_clause(cursor, user_id)
2457             cursor.execute(f"""
2458                 SELECT * FROM jobs WHERE {scope_clause}
2459                 ORDER BY found_date DESC
2460             """, (user_id,))
2461             all_jobs = [dict(r) for r in cursor.fetchall()]
```

### 17. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3547`](./app.py#L3547)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3546 
3547         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
3548         cursor.execute(search_query, params)
```

### 18. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:5172`](./app.py#L5172)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
5171                     with open('token.pickle', 'rb') as token:
5172                         creds = pickle.load(token)
5173                     if creds and creds.expired and creds.refresh_token:
```

### 19. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:5663`](./app.py#L5663)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
5662             with open('token.pickle', 'rb') as token:
5663                 creds = pickle.load(token)
5664
```

### 20. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:6697`](./app.py#L6697)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
6696     with open(token_path, 'rb') as token_file:
6697         creds = pickle.load(token_file)
6698
```

### 21. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:7391`](./app.py#L7391)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
7390         return False
7391     return hostname.strip().lower() in ('localhost', '127.0.0.1', '0.0.0.0', '::1')
7392
```

### 22. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:12153`](./app.py#L12153)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
12152     logger.info(f"Starting Flask application on 0.0.0.0:{port} (debug={debug_mode})...")
12153     app.run(debug=debug_mode, host='0.0.0.0', port=port)
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

### 26. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./send_launch_emails.py:163`](./send_launch_emails.py#L163)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
162     with open(token_path, "rb") as token:
163         creds = pickle.load(token)
164
```

### 27. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:45`](./ai_utils.py#L45)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
44         return json.loads(text)
45     except Exception:
46         pass
47
```

### 28. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./ai_utils.py:59`](./ai_utils.py#L59)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
58             return json.loads(cand)
59         except Exception:
60             continue
61
```

### 29. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:69`](./ai_utils.py#L69)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
68             return json.loads(sub)
69         except Exception:
70             pass
71
```

### 30. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:79`](./ai_utils.py#L79)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
78             return json.loads(sub)
79         except Exception:
80             pass
81
```

### 31. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./app.py:12`](./app.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import os
12 import pickle
13 import random
```

### 32. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1197`](./app.py#L1197)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1196                 conn.rollback()
1197             except Exception:
1198                 pass
1199         try:
```

### 33. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1208`](./app.py#L1208)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1207                 conn.rollback()
1208             except Exception:
1209                 pass
1210         cursor.execute("""
```

### 34. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1514`](./app.py#L1514)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1513                 conn.rollback()
1514             except Exception:
1515                 pass
1516             logger.warning(f"Username already exists: {clean_username}")
```

### 35. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1565`](./app.py#L1565)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1564                 conn.rollback()
1565             except Exception:
1566                 pass
1567             return False, 'That username is already taken. Try one of the suggestions below.'
```

### 36. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1650`](./app.py#L1650)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1649                         conn.rollback()
1650                     except Exception:
1651                         pass
1652             if clean_sub and not (current_sub or '').strip():
```

### 37. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1659`](./app.py#L1659)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1658                         conn.rollback()
1659                     except Exception:
1660                         pass
1661             if clean_avatar and clean_avatar != (current_avatar or '').strip():
```

### 38. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1668`](./app.py#L1668)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1667                         conn.rollback()
1668                     except Exception:
1669                         pass
1670         except Exception as e:
```

### 39. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1855`](./app.py#L1855)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1854                 conn.rollback()
1855             except Exception:
1856                 pass
1857             logger.error(f"Error batch-adding jobs to database: {e}")
```

### 40. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:2856`](./app.py#L2856)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
2855                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
2856                 except Exception:
2857                     continue
2858
```

### 41. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:3413`](./app.py#L3413)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
3412                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
3413                     except Exception:
3414                         pass
3415                 conn.commit()
```

### 42. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:3605`](./app.py#L3605)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
3604                         ))
3605                     except Exception:
3606                         pass
3607                 conn.commit()
```

### 43. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3755`](./app.py#L3755)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3754             options.add_argument('--disable-dev-shm-usage')
3755             random_user_agent = random.choice(USER_AGENTS)
3756             options.add_argument(f"user-agent={random_user_agent}")
```

### 44. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4047`](./app.py#L4047)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4046             }
4047             headers = {'User-Agent': random.choice(USER_AGENTS)}
4048             try:
```

### 45. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4050`](./app.py#L4050)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4049                 if page > 0:
4050                     time.sleep(random.uniform(*self.request_delay))
4051                 response = session.get(base_url, params=params, headers=headers, timeout=self.http_timeout)
```

### 46. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4149`](./app.py#L4149)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4148                 )
4149                 detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
4150                 time.sleep(random.uniform(*self.linkedin_detail_delay))
```

### 47. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4150`](./app.py#L4150)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4149                 detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
4150                 time.sleep(random.uniform(*self.linkedin_detail_delay))
4151                 resp = self._get_http_session().get(detail_url, headers=detail_headers, timeout=self.http_timeout)
```

### 48. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4232`](./app.py#L4232)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4231                 headers = {
4232                     'User-Agent': random.choice(USER_AGENTS),
4233                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 49. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4237`](./app.py#L4237)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4236                 if page > 1:
4237                     time.sleep(random.uniform(*self.request_delay))
4238
```

### 50. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4451`](./app.py#L4451)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4450             logger.debug(f"[Internshala] Fetching details: {link}")
4451             time.sleep(random.uniform(*self.internshala_detail_delay))
4452
```

### 51. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4454`](./app.py#L4454)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4453             headers = {
4454                 'User-Agent': random.choice(USER_AGENTS),
4455                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 52. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:5763`](./app.py#L5763)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
5762                                 row[rel_col-1].value = f"🔴 {val}"
5763                         except:
5764                             continue
5765                 # --- Make Links Clickable and Button Style ---
```

### 53. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:6332`](./app.py#L6332)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
6331                             os.remove(excel_file)
6332                         except Exception:
6333                             pass
6334
```

### 54. [ℹ️ LOW] Possible hardcoded password: 'token.pickle'
- **File:** [`./app.py:6692`](./app.py#L6692)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
6691     """Send a MIME message via existing non-interactive Gmail OAuth credentials."""
6692     token_path = 'token.pickle'
6693     if not os.path.exists(token_path):
```

### 55. [ℹ️ LOW] Possible hardcoded password: 'https://oauth2.googleapis.com/token'
- **File:** [`./app.py:7426`](./app.py#L7426)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
7425             'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
7426             'token_uri': 'https://oauth2.googleapis.com/token',
7427             'redirect_uris': [callback_uri],
7428         }
7429     }
7430     os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')
7431     # Request only non-sensitive identity scopes on standard sign-in so Google displays
7432     # verified branding without the "Google hasn't verified this app" sensitive-scope warning.
7433     include_sensitive = os.environ.get('GOOGLE_OAUTH_INCLUDE_SENSITIVE_SCOPES', '0').lower() in ('1', 'true', 'yes')
```

### 56. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:8459`](./app.py#L8459)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
8458                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
8459             except Exception:
8460                 pass
8461
```

### 57. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:10384`](./app.py#L10384)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
10383     fake_analysis_data = {
10384         "monthly_visits": f"{random.randint(50, 500)}K",
10385         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 58. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:10385`](./app.py#L10385)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
10384         "monthly_visits": f"{random.randint(50, 500)}K",
10385         "bounce_rate": f"{random.randint(30, 70)}%",
10386         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 59. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:10386`](./app.py#L10386)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
10385         "bounce_rate": f"{random.randint(30, 70)}%",
10386         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
10387     }
```

### 60. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:10924`](./app.py#L10924)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
10923                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
10924             except Exception:
10925                 pass
10926             return jsonify({
```

### 61. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:12006`](./app.py#L12006)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
12005                 user_name = user_details.get('full_name')
12006         except Exception:
12007             pass
12008
```

### 62. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:48`](./outreach_scraper.py#L48)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
47         self.session = requests.Session()
48         self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
49         self.scraped_domains = set()
```

### 63. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:108`](./outreach_scraper.py#L108)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
107         # Add random delay to appear more human
108         time.sleep(random.uniform(self.min_delay, self.max_delay))
109
```

### 64. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./scripts/proc_runner.py:14`](./scripts/proc_runner.py#L14)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
13 import os
14 import subprocess
15 import sys
```

### 65. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:293`](./scripts/proc_runner.py#L293)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
292             sys.stderr.flush()
293         except Exception:
294             pass
295         if job_handle:
```

### 66. [ℹ️ LOW] Starting a process with a partial executable path
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

### 67. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
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

### 68. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:306`](./scripts/proc_runner.py#L306)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
305                 )
306             except Exception:
307                 pass
308             try:
```

### 69. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:310`](./scripts/proc_runner.py#L310)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
309                 proc.kill()
310             except Exception:
311                 pass
312         os._exit(0)
```

### 70. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./scripts/proc_runner.py:332`](./scripts/proc_runner.py#L332)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
331 
332         proc = subprocess.Popen(cmd, env=env, cwd=str(REPO_ROOT))
333         if child_job is not None:
```

### 71. [ℹ️ LOW] Starting a process without a shell.
- **File:** [`./scripts/proc_runner.py:398`](./scripts/proc_runner.py#L398)
- **Rule ID:** `B606` (start_process_with_no_shell)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b606_start_process_with_no_shell.html)

```python
397         os.chdir(REPO_ROOT)
398         os.execvpe(cmd[0], cmd, env)
399
```

### 72. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./send_launch_emails.py:12`](./send_launch_emails.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import base64
12 import pickle
13 import argparse
```

### 73. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./send_launch_emails.py:259`](./send_launch_emails.py#L259)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
258         role = c.get("Role_Category", "your domain")
259         ticket_id = c.get("TicketId") or c.get("PassCode") or f"JS-{random.randint(1000, 9999)}"
260         subject = tmpl["subject"].format(name=name, role=role)
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
