# Kirana AI Operating System — Hindsight AI Memory Specification

## 1. Role of Hindsight Memory

Hindsight is the long-term AI memory layer for Kirana shopkeepers.

PostgreSQL stores **factual business records** (exact sale items, current stock, payment balances).
Hindsight stores **experiential and contextual memory** (shopkeeper order habits, supplier delivery quirks, recommendation decision history).

---

## 2. Memory Categories

1. `OWNER_PREFERENCE`: e.g., *"Main Maggi ek baar mein 35 se zyada order nahi karta."*
2. `BUSINESS_DECISION`: e.g., *"Accepted supplier order for 30 units on Thursday."*
3. `CUSTOMER_PATTERN`: e.g., *"Customer Ramesh clears his Khata balance on the 5th of every month."*
4. `SUPPLIER_BEHAVIOR`: e.g., *"Supplier B takes 4 days to deliver on weekends."*
5. `RECOMMENDATION_OUTCOME`: e.g., *"30-unit Maggi restock recommendation modified from 40 to 30 was successful."*

---

## 3. The Core Memory Loop

```
  [ OBSERVE ]  (Real-time Sales & Inventory Facts)
       │
       ▼
  [ REMEMBER ] (Store Owner Preferences & Decision Outcomes in Hindsight)
       │
       ▼
  [ RECALL ]   (Search Hindsight Context during Assistant Queries)
       │
       ▼
  [ REASON ]   (Gemini synthesizes DB facts + ML predictions + Memories)
       │
       ▼
  [ RECOMMEND] (Actionable Hinglish Restock & Pricing Advice)
       │
       ▼
  [ DECISION ] (Owner accepts, rejects, or modifies recommendation)
       │
       ▼
  [ OUTCOME ]  (Track real-world sales performance of decision)
       │
       ▼
  [ LEARN ]    (Feed outcome feedback back into Hindsight)
```
