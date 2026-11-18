# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-18 09:33:25 UTC`  
> **Branch/Ref:** `main` (`4bafea88`)  

## 📊 Executive Summary

| Category | Findings | Severity Note |
| :--- | :--- | :--- |
| **🚨 High Severity (Code)** | `8` | Critical flaws, injection, or hardcoded secrets |
| **⚠️ Medium Severity (Code)** | `15` | Weak crypto, insecure configs, or unvalidated parameters |
| **ℹ️ Low Severity (Code)** | `43` | Information leaks or minor code hygiene warnings |
| **📦 Known CVEs (Dependencies)** | `0` | Vulnerabilities identified in third-party packages |
| **Total Security Items** | `66` | Combined code & dependency signals |

## 🔍 Code Security Vulnerabilities (SAST)

Identified `66` code security items across Python source files:

### 1. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1508`](./app.py#L1508)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1507         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
1508         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1509
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:2297`](./app.py#L2297)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
2296                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
2297                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
2298                 if new_hash != old_hash:
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:4324`](./app.py#L4324)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
4323             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
4324             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
4325             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:8269`](./app.py#L8269)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
8268                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
8269                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
8270                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:8566`](./app.py#L8566)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
8565                             if contact_data.get('email'):
8566                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
8567                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:8570`](./app.py#L8570)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
8569                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
8570                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
8571                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:8686`](./app.py#L8686)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
8685     if not linkedin_url:
8686         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
8687         linkedin_url = f"manual-entry-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:8759`](./app.py#L8759)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
8758                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
8759                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
8760                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 9. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1646`](./app.py#L1646)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1645         scope_clause = self._user_scope_clause(cursor, user_id)
1646         query = f"SELECT {query_columns} FROM jobs WHERE {scope_clause}"
1647         params = [user_id]
```

### 10. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1702`](./app.py#L1702)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1701 
1702         count_query = f"SELECT COUNT(*) FROM ({query}) AS filtered_jobs_count"
1703         cursor.execute(count_query, params)
```

### 11. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1891`](./app.py#L1891)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1890             placeholders = ','.join(['?'] * len(job_ids))
1891             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
1892             deleted_count = cursor.rowcount
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1933`](./app.py#L1933)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1932             scope_clause = self._user_scope_clause(cursor, user_id)
1933             cursor.execute(f"SELECT status, COUNT(*) FROM jobs WHERE {scope_clause} AND status IS NOT NULL GROUP BY status", (user_id,))
1934             rows = cursor.fetchall()
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2174`](./app.py#L2174)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2173             scope_clause = self._user_scope_clause(cursor, user_id)
2174             cursor.execute(f"""
2175                 SELECT * FROM jobs WHERE {scope_clause}
2176                 ORDER BY found_date DESC
2177             """, (user_id,))
2178             all_jobs = [dict(r) for r in cursor.fetchall()]
```

### 14. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3264`](./app.py#L3264)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3263 
3264         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
3265         cursor.execute(search_query, params)
```

### 15. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4766`](./app.py#L4766)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4765                     with open('token.pickle', 'rb') as token:
4766                         creds = pickle.load(token)
4767                     if creds and creds.expired and creds.refresh_token:
```

### 16. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:5257`](./app.py#L5257)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
5256             with open('token.pickle', 'rb') as token:
5257                 creds = pickle.load(token)
5258
```

### 17. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:6273`](./app.py#L6273)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
6272     with open(token_path, 'rb') as token_file:
6273         creds = pickle.load(token_file)
6274
```

### 18. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:6967`](./app.py#L6967)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
6966         return False
6967     return hostname.strip().lower() in ('localhost', '127.0.0.1', '0.0.0.0', '::1')
6968
```

### 19. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:11207`](./app.py#L11207)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
11206     logger.info(f"Starting Flask application on 0.0.0.0:{port} (debug={debug_mode})...")
11207     app.run(debug=debug_mode, host='0.0.0.0', port=port)
```

### 20. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
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

### 21. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./scripts/migrate_sqlite_to_postgres.py:116`](./scripts/migrate_sqlite_to_postgres.py#L116)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
115     )
116     source_cursor = source.execute(f'SELECT * FROM "{table}"')
117     copied = 0
```

### 22. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./scripts/proc_runner.py:120`](./scripts/proc_runner.py#L120)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
119     debug = _is_truthy(os.environ.get("FLASK_DEBUG") or os.environ.get("DEBUG"))
120     app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
121     return 0
```

### 23. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./send_launch_emails.py:163`](./send_launch_emails.py#L163)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
162     with open(token_path, "rb") as token:
163         creds = pickle.load(token)
164
```

### 24. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:26`](./ai_utils.py#L26)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
25         return json.loads(text)
26     except Exception:
27         pass
28
```

### 25. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./ai_utils.py:40`](./ai_utils.py#L40)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
39             return json.loads(cand)
40         except Exception:
41             continue
42
```

### 26. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:50`](./ai_utils.py#L50)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
49             return json.loads(sub)
50         except Exception:
51             pass
52
```

### 27. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:60`](./ai_utils.py#L60)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
59             return json.loads(sub)
60         except Exception:
61             pass
62
```

### 28. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./app.py:12`](./app.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import os
12 import pickle
13 import random
```

### 29. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1090`](./app.py#L1090)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1089                 conn.rollback()
1090             except Exception:
1091                 pass
1092         cursor.execute("""
```

### 30. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1391`](./app.py#L1391)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1390                 conn.rollback()
1391             except Exception:
1392                 pass
1393             logger.warning(f"Username already exists: {clean_username}")
```

### 31. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:1442`](./app.py#L1442)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
1441                 conn.rollback()
1442             except Exception:
1443                 pass
1444             return False, 'That username is already taken. Try one of the suggestions below.'
```

### 32. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:2573`](./app.py#L2573)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
2572                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
2573                 except Exception:
2574                     continue
2575
```

### 33. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:3130`](./app.py#L3130)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
3129                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
3130                     except Exception:
3131                         pass
3132                 conn.commit()
```

### 34. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:3322`](./app.py#L3322)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
3321                         ))
3322                     except Exception:
3323                         pass
3324                 conn.commit()
```

### 35. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3462`](./app.py#L3462)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3461             options.add_argument('--disable-dev-shm-usage')
3462             random_user_agent = random.choice(USER_AGENTS)
3463             options.add_argument(f"user-agent={random_user_agent}")
```

### 36. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3684`](./app.py#L3684)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3683             }
3684             headers = {'User-Agent': random.choice(USER_AGENTS)}
3685             try:
```

### 37. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3687`](./app.py#L3687)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3686                 logger.info(f"[LinkedIn] Sending request to LinkedIn for job list (page {page + 1})...")
3687                 time.sleep(random.uniform(*self.request_delay))  # Dynamic delay based on scan mode
3688                 response = requests.get(base_url, params=params, headers=headers, timeout=15, proxies=proxies)
```

### 38. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3755`](./app.py#L3755)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3754                         logger.info(f"[LinkedIn] Fetching job detail page: {job['link']}")
3755                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3756                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
```

### 39. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3756`](./app.py#L3756)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3755                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3756                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
3757                         resp = requests.get(job['link'], headers=detail_headers, timeout=15)
```

### 40. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3833`](./app.py#L3833)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3832             session.headers.update({
3833                 'User-Agent': random.choice(USER_AGENTS),
3834                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
```

### 41. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3855`](./app.py#L3855)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3854                     # Randomized delay to avoid detection
3855                     time.sleep(random.uniform(*self.request_delay))
3856
```

### 42. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4055`](./app.py#L4055)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4054             # Randomized delay
4055             time.sleep(random.uniform(1.5, 3.5))
4056
```

### 43. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:4058`](./app.py#L4058)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
4057             headers = {
4058                 'User-Agent': random.choice(USER_AGENTS),
4059                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 44. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:5357`](./app.py#L5357)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
5356                                 row[rel_col-1].value = f"🔴 {val}"
5357                         except:
5358                             continue
5359                 # --- Make Links Clickable and Button Style ---
```

### 45. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5939`](./app.py#L5939)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5938                 logger.info(f"Cleaned up Excel report: {excel_file}.")
5939             except Exception:
5940                 pass
5941
```

### 46. [ℹ️ LOW] Possible hardcoded password: 'token.pickle'
- **File:** [`./app.py:6268`](./app.py#L6268)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
6267     """Send a MIME message via existing non-interactive Gmail OAuth credentials."""
6268     token_path = 'token.pickle'
6269     if not os.path.exists(token_path):
```

### 47. [ℹ️ LOW] Possible hardcoded password: 'https://oauth2.googleapis.com/token'
- **File:** [`./app.py:7002`](./app.py#L7002)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
7001             'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
7002             'token_uri': 'https://oauth2.googleapis.com/token',
7003             'redirect_uris': [callback_uri],
7004         }
7005     }
7006     os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')
7007     oauth_scopes = [
7008         'openid',
7009         'https://www.googleapis.com/auth/userinfo.email',
```

### 48. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:7943`](./app.py#L7943)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
7942                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
7943             except Exception:
7944                 pass
7945
```

### 49. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:9072`](./app.py#L9072)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
9071         conn.close()
9072     except Exception as e:
9073         pass
9074
```

### 50. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:9438`](./app.py#L9438)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
9437     fake_analysis_data = {
9438         "monthly_visits": f"{random.randint(50, 500)}K",
9439         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 51. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:9439`](./app.py#L9439)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
9438         "monthly_visits": f"{random.randint(50, 500)}K",
9439         "bounce_rate": f"{random.randint(30, 70)}%",
9440         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 52. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:9440`](./app.py#L9440)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
9439         "bounce_rate": f"{random.randint(30, 70)}%",
9440         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
9441     }
```

### 53. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:9978`](./app.py#L9978)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
9977                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
9978             except Exception:
9979                 pass
9980             return jsonify({
```

### 54. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:11060`](./app.py#L11060)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
11059                 user_name = user_details.get('full_name')
11060         except Exception:
11061             pass
11062
```

### 55. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:48`](./outreach_scraper.py#L48)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
47         self.session = requests.Session()
48         self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
49         self.scraped_domains = set()
```

### 56. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:108`](./outreach_scraper.py#L108)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
107         # Add random delay to appear more human
108         time.sleep(random.uniform(self.min_delay, self.max_delay))
109
```

### 57. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./scripts/proc_runner.py:14`](./scripts/proc_runner.py#L14)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
13 import os
14 import subprocess
15 import sys
```

### 58. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:293`](./scripts/proc_runner.py#L293)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
292             sys.stderr.flush()
293         except Exception:
294             pass
295         if job_handle:
```

### 59. [ℹ️ LOW] Starting a process with a partial executable path
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

### 60. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
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

### 61. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:306`](./scripts/proc_runner.py#L306)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
305                 )
306             except Exception:
307                 pass
308             try:
```

### 62. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:310`](./scripts/proc_runner.py#L310)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
309                 proc.kill()
310             except Exception:
311                 pass
312         os._exit(0)
```

### 63. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./scripts/proc_runner.py:332`](./scripts/proc_runner.py#L332)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
331 
332         proc = subprocess.Popen(cmd, env=env, cwd=str(REPO_ROOT))
333         if child_job is not None:
```

### 64. [ℹ️ LOW] Starting a process without a shell.
- **File:** [`./scripts/proc_runner.py:398`](./scripts/proc_runner.py#L398)
- **Rule ID:** `B606` (start_process_with_no_shell)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b606_start_process_with_no_shell.html)

```python
397         os.chdir(REPO_ROOT)
398         os.execvpe(cmd[0], cmd, env)
399
```

### 65. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./send_launch_emails.py:12`](./send_launch_emails.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import base64
12 import pickle
13 import argparse
```

### 66. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
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
