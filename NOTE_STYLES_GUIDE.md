# Note Styles Feature Guide

## Overview

The PDF Notes API now supports **three different note styles** to match your reading and learning preferences. Choose the style that works best for you!

## 📝 Available Note Styles

### 1. **Short** - Quick & Simple
*Perfect for: Quick reviews, study flashcards, busy schedules*

**What you get:**
- Simple bullet points only
- Just the most important facts
- Each point is one easy sentence
- 5-7 points per section
- No extra details or explanations

**Example:**
```
• Machine learning uses data to make predictions
• Neural networks learn patterns from examples
• Training requires lots of data and computing power
• Deep learning works best for images and text
• Models improve with more training data
```

**Best for:**
- Quick reference guides
- Exam preparation
- Key takeaways
- Time-sensitive reading

---

### 2. **Moderate** - Balanced & Clear ⭐ (Default)
*Perfect for: General learning, regular study, most use cases*

**What you get:**
- Mix of bullet points and short paragraphs
- Main ideas with important details
- Brief explanations in simple terms
- Organized by topics
- Examples when helpful

**Example:**
```
## Machine Learning Basics

Machine learning is a way for computers to learn from data and make 
predictions without being explicitly programmed. The system looks at 
examples and finds patterns.

Key components:
• Data - The examples the system learns from
• Model - The pattern-finding algorithm
• Training - The learning process
• Prediction - Using learned patterns on new data

Neural networks are a popular type of machine learning that mimics 
how the brain works. They excel at tasks like image recognition 
and language processing.
```

**Best for:**
- Regular studying
- Professional development
- Understanding concepts
- Most documents

---

### 3. **Descriptive** - Detailed & Complete
*Perfect for: Deep learning, complex topics, thorough understanding*

**What you get:**
- Full paragraphs with complete explanations
- All important information included
- Everything explained in simple language
- Clear sections with headings
- Examples and context
- Background information

**Example:**
```
## Understanding Machine Learning

Machine learning is a field of artificial intelligence that enables 
computers to learn from data and make decisions without being explicitly 
programmed for every scenario. Instead of following fixed rules, machine 
learning systems analyze examples (called training data) to identify 
patterns and relationships.

### How It Works

The learning process involves feeding the system many examples along 
with the correct answers. Over time, the system learns to recognize 
patterns that connect the input data to the desired output. For instance, 
if we want to teach a computer to recognize cats in photos, we show it 
thousands of cat pictures labeled as "cat" and non-cat pictures labeled 
"not cat."

### Types of Machine Learning

There are several approaches to machine learning:

**Supervised Learning**: The system learns from labeled examples where 
we already know the correct answer. This is like learning with a teacher 
who tells you if you're right or wrong.

**Unsupervised Learning**: The system finds patterns in data without 
being told what to look for. This is like exploring and discovering 
things on your own.

**Neural Networks**: A special type of machine learning inspired by how 
the human brain works. These are particularly good at tasks like 
recognizing images, understanding speech, and translating languages...
```

**Best for:**
- Research papers
- Technical documentation
- Complex subjects
- Comprehensive understanding
- Teaching materials

---

## 🚀 How to Use

### API Request (cURL)

```bash
# Short style
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf" \
  -F "note_style=short"

# Moderate style (default)
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf" \
  -F "note_style=moderate"

# Descriptive style
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf" \
  -F "note_style=descriptive"
```

### Python Client

```python
import requests

# Upload with short style
response = requests.post(
    "http://localhost:8000/upload",
    files={'file': open('document.pdf', 'rb')},
    data={'note_style': 'short'}
)

# Upload with descriptive style
response = requests.post(
    "http://localhost:8000/upload",
    files={'file': open('document.pdf', 'rb')},
    data={'note_style': 'descriptive'}
)
```

### API Documentation

Visit http://localhost:8000/docs to use the interactive API interface with a dropdown menu to select your preferred note style.

---

## 💡 Choosing the Right Style

### Use **Short** when you:
- Need quick facts only
- Are short on time
- Want to review key points
- Need a summary card
- Are preparing for a quiz

### Use **Moderate** when you:
- Want balanced information
- Need to understand the topic
- Are studying regularly
- Want clear organization
- Need both overview and details

### Use **Descriptive** when you:
- Need deep understanding
- Are reading complex material
- Want comprehensive notes
- Need teaching materials
- Are doing research

---

## 🎯 Combining with Custom Prompts

You can combine note styles with your own instructions for even better results!

### Example 1: Short + Custom Focus
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@research.pdf" \
  -F "note_style=short" \
  -F "user_prompt=Focus only on the methodology"
```
Result: Quick bullet points about methodology only

### Example 2: Descriptive + Custom Focus
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@textbook.pdf" \
  -F "note_style=descriptive" \
  -F "user_prompt=Include lots of examples for each concept"
```
Result: Detailed notes with many examples

### Example 3: Moderate + Custom Organization
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@article.pdf" \
  -F "note_style=moderate" \
  -F "user_prompt=Organize by problem, solution, and results"
```
Result: Balanced notes organized in specified structure

---

## 📊 What Happens Behind the Scenes

### For Each Style, the AI:

**Short Style:**
- Extracts only critical information
- Uses ~300 tokens per chunk
- Creates concise bullet points
- Focuses on key facts
- Minimal final synthesis

**Moderate Style:**
- Balances detail and brevity
- Uses ~500 tokens per chunk
- Mixes bullets and paragraphs
- Includes context and examples
- Organized final synthesis

**Descriptive Style:**
- Includes comprehensive information
- Uses ~800 tokens per chunk
- Full paragraph explanations
- Rich context and examples
- Detailed hierarchical synthesis

---

## 🔧 Technical Details

### Token Limits by Style

| Style | Per Chunk | Final Note | Total Estimate |
|-------|-----------|------------|----------------|
| Short | 300 | 900 | ~1,200 |
| Moderate | 500 | 1,500 | ~2,000 |
| Descriptive | 800 | 2,400 | ~3,200 |

*Note: Actual token usage varies based on content complexity*

### Processing Time

- **Short**: Fastest (fewer tokens to generate)
- **Moderate**: Normal (balanced processing)
- **Descriptive**: Longer (more comprehensive output)

### API Cost Implications

If using paid LLM APIs (OpenAI):
- Short style uses fewer tokens = lower cost
- Descriptive style uses more tokens = higher cost

With free tier (Gemini):
- All styles work within free limits
- Longer documents might hit daily quota faster with descriptive style

---

## 📚 Use Case Examples

### Research Paper
- **Short**: Quick bullet points of findings
- **Moderate**: Summary with methodology and results
- **Descriptive**: Complete overview with background, methods, results, and implications

### Textbook Chapter
- **Short**: Key concepts to memorize
- **Moderate**: Study notes with explanations
- **Descriptive**: Comprehensive teaching notes

### Business Report
- **Short**: Executive summary points
- **Moderate**: Main findings and recommendations
- **Descriptive**: Full analysis with context

### Legal Document
- **Short**: Key clauses and dates
- **Moderate**: Important terms and obligations
- **Descriptive**: Complete summary with implications

---

## ❓ Frequently Asked Questions

### Can I change the style after uploading?
No, you need to upload again with the new style. Each upload is processed with the selected style.

### Which style is best?
It depends on your needs! Most users find **Moderate** works well for general use. Try different styles to see what you prefer.

### Can I get all three styles for one document?
Yes! Upload the same document three times with different styles to compare.

### Do all styles work with RAG Q&A?
Yes! The question-answering feature works the same regardless of note style.

### Does the style affect processing time?
Slightly. Descriptive notes take a bit longer because they generate more content.

### What if I don't specify a style?
The system uses **Moderate** by default - it's the balanced option.

---

## 🎓 Best Practices

1. **Start with Moderate** - Try the default balanced style first
2. **Match to Purpose** - Use short for quick reference, descriptive for learning
3. **Combine with Prompts** - Add custom instructions for best results
4. **Test Different Styles** - Try all three on a sample document
5. **Consider Audience** - Use descriptive for teaching, short for presentations

---

## 🔄 Example Workflow

```python
# Upload the same document with different styles for comparison
import requests

pdf_file = 'important_document.pdf'

# Get quick version
short = requests.post(
    "http://localhost:8000/upload",
    files={'file': open(pdf_file, 'rb')},
    data={'note_style': 'short'}
)

# Get balanced version
moderate = requests.post(
    "http://localhost:8000/upload",
    files={'file': open(pdf_file, 'rb')},
    data={'note_style': 'moderate'}
)

# Get detailed version
descriptive = requests.post(
    "http://localhost:8000/upload",
    files={'file': open(pdf_file, 'rb')},
    data={'note_style': 'descriptive'}
)

# Compare results after processing completes
```

---

## 💬 Need Help?

- Visit the API docs: http://localhost:8000/docs
- Check the main README: [README.md](README.md)
- Review API guide: [API_GUIDE.md](API_GUIDE.md)

**Remember**: The best note style is the one that helps YOU learn and work most effectively! 📚✨
