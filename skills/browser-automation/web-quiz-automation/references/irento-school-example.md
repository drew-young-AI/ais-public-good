# Example: Automating iRent School Quizzes

This section documents the specific steps taken to automate the iRent School quizzes (申辦會員, 服務說明, 積分與徽章, 預授權, 和雲錢包) using the kimi-webbridge tool.

## Session Setup

Each quiz section was handled in a separate browser tab but under the same session name (`irent-all-quiz`) to keep them grouped.

## Common Pattern

For each section:
1. Navigate to the section URL (or click from the main page).
2. Take a snapshot to get the accessibility tree.
3. Identify the correct answers by reading the question and options.
4. Click each answer by matching the exact text content (using JavaScript evaluation).
5. Click the submit button.
6. Verify success by checking for a confirmation message.
7. Navigate to the next section or return to the main page.

## Answer Selection Method

Due to dynamic class names and potential changes in the DOM, the following JavaScript snippet was used to click an element by its exact visible text:

```javascript
(() => {
  const targetText = "Exact answer text"; // e.g., "學生證"
  const elements = Array.from(document.querySelectorAll('*'));
  for (const el of elements) {
    if (el.textContent.trim() === targetText && el.children.length === 0) {
      el.click();
      return true;
    }
  }
  return false;
})()
```

This method was preferred over using `@e` refs from the snapshot because the text content is more directly tied to the answer and less likely to change with minor UI updates.

## Section-Specific Notes

- **申辦會員**: Answers were B, A, B, D, D (as per the transcript).
- **服務說明**: Focused on service explanations, answers selected based on the provided material.
- **積分與徽章**: Questions about credit points and badges.
- **預授權**: Questions about pre-authorization for reservations.
- **和雲錢包**: Questions about the iRent wallet.

## Cleanup

After completing all sections, the session was closed with `close_session` to remove the tab group.

## References

- The full transcript of the automation session is available in the conversation history.
- For more on kimi-webbridge, see the kimi-webbridge skill.

---