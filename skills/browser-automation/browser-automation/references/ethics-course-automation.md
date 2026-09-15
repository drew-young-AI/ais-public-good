# Ethics Course Automation via Hermes Browser Automation

This reference documents the steps used to automate reading an ethics course module and passing its post-test using Hermes browser automation (Chrome via CDP).

## Workflow Overview

1. Navigate to course list: https://ethics-p.moe.edu.tw/courses/my/
2. Identify unread courses (those without a checkmark or with "尚未修習完畢").
3. Click the course link to launch the course iframe.
4. Within the course iframe, navigate through the units (e.g., "單元簡介", "1. 案例思考", etc.) until reaching the "課後測驗" (post-test).
5. Switch to the inner iframe containing the test questions.
6. Answer each question by selecting the correct radio option (based on known correct answers or by reading the explanations).
7. Submit the test and verify the result shows all answers correct.

## Detailed Steps (as performed in the session)

### Step 1: Load the course list
```bash
browser_navigate https://ethics-p.moe.edu.tw/courses/my/
```

### Step 2: Identify an unread course
From the snapshot, we saw rows with links like:
- `0101_學術研究倫理定義與內涵` (already read)
- `0707_行為和社會科學研究倫理概論` (unread at the time)

We selected the course with ID `35` (as seen in the URL `startcourse/?t=35`) which corresponds to "0707_行為和社會科學研究倫理概論".

### Step 3: Launch the course
Click the course link (ref `e107` in the snapshot) which executes `showCourse('35')` and opens an iframe.

### Step 4: Navigate through the course units
Inside the outer iframe (`course_frame`) we clicked the following links in order:
- `e49` → "單元簡介"
- `e50` → "1. 案例思考"
- `e51` → "2.1 定義與相關倫理議題"
- Continuing through the unit list until the "課後測驗" link (`e60`).

### Step 5: Switch to the test iframe
After clicking "課後測驗", the inner iframe (`item`) loaded `test.html`. We then navigated directly to:
https://ethics-p.moe.edu.tw/static/ethics/u20/test.html

### Step 6: Answer the test questions
The test consisted of 5 multiple-choice questions. We selected the following options (1-indexed radio groups):
- Q1: Option 3 (ref `e4`)
- Q2: Option 4 (ref `e9`)
- Q3: Option 4 (ref `e13`)
- Q4: Option 2 (ref `e15`)
- Q5: Option 4 (ref `e21`)

These selections were made via `browser_click` on the corresponding radio refs.

### Step 7: Submit and verify
Clicked the "送出" button (ref `e22`). The browser navigated to a result page (`test_ans.html?a=1:3,2:4,3:4,4:2,5:4`) showing that all answers were correct.

## Notes for Reuse

- The course structure (unit links and test URL pattern) is consistent across modules in this site.
- To automate multiple courses, iterate over the course table rows, extract the course ID from the `onclick="showCourse('X')"`, launch the course, and repeat the unit navigation.
- The test answers may vary per course; however, the site often provides explanations after each question, allowing the agent to infer the correct answer by reading the explanation text.
- Using `browser_console` to extract text from explanation elements can be combined with simple logic to map explanation to correct option.

## References

- The site's JavaScript functions: `showCourse(id)`, `showCourseById(id)`.
- The test answer verification endpoint: `static/ethics/u20/test_ans.html`.
