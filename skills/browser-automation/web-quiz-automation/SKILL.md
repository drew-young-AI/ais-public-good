---
name: web-quiz-automation
type: skill
description: Automate online quizzes via text-based interaction.
version: 1.0.0
---
# Web Quiz Automation

Automate quiz completion and form filling on websites using tools like kimi-webbridge.
Focuses on robust, text-based interaction to overcome fragile CSS selectors.

## When to Use

Use when you need to:
- Complete multi-section online quizzes (like iRent School)
- Fill forms where element selectors may change
- Automate repetitive web-based assessments
- Work with websites that provide accessibility trees or semantic element references

## Workflow Overview

1. **Navigate to the starting page**  
   Use `navigate` with `newTab:true` and a meaningful `group_title` and `session` name.

2. **Get the accessibility tree**  
   Use `snapshot` to obtain the AX tree with `@e` refs and text content.

3. **Identify and click answers**  
   - Extract answer text from the quiz content (from the tree or provided answers)
   - Use JavaScript evaluation to click elements by exact text match (more reliable than selectors)
   - Example code snippet:
     ```javascript
     (() => {
       const targetText = "Correct Answer Text";
       const els = Array.from(document.querySelectorAll('*'));
       for (const el of els) {
         if (el.textContent.trim() === targetText && el.children.length === 0) {
           el.click();
           return true;
         }
       }
       return false;
     })()
     ```

4. **Submit the form**  
   Locate the submit button by text (e.g., "提交答案", "Submit") and click it.

5. **Verify completion**  
   After submission, snapshot again to check for success messages (e.g., "恭喜通過測驗！").

6. **Handle multi-section quizzes**  
   - Keep the same `session` name across all sections
   - To advance: either click navigation links (e.g., "前往下一單元") or navigate directly to the next section URL
   - When finished, use `close_session` to clean up the tab group

## Tips and Pitfalls

- **Text matching is more stable** than CSS selectors for dynamic sites.
- Always verify clicks by checking post-action state (snapshot again).
- If an element is not clickable via text match, fall back to `@e` refs from the snapshot.
- For iframe content, navigate directly to the iframe URL if needed.
- Some sites may block synthetic events; in such cases, consider alternative approaches.
- Maintain a consistent `session` name to keep related tabs grouped.

## Example: iRent School Quiz Automation

See the session transcript for a full example of automating the iRent School quizzes (申辦會員, 服務說明, 積分與徽章, 預授權, 和雲錢包).

## Reference

- [kimi-webbridge skill](kimi-webbridge) for the underlying browser control tool
- [browser-automation] for general browser automation concepts

---