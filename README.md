# Improving-LLMs-on-underrepresented-programming-languages

Test task

## Task

In the test assignment, we suggest you to work on the code completion task:

- Pick a large open-source project, written mostly in Kotlin, e.g. Kotlin
- Extract all code in Kotlin from the project to create a Kotlin code completion dataset
- Adapt a Python-oriented pre-trained Transformer model such as Phi-2 to do code completion and evaluate it on the Kotlin dataset test part and CodeXGLUE Python code completion test part (prompts, answers)
- Fine-tune the model on the Kotlin dataset you have collected
- Report the changes of quality on both Kotlin and Python data after the finetuning

## Dataset

To create the dataset, I took the [Kotlin](https://github.com/JetBrains/kotlin) project and extracted all files with the `.kt` extension. This resulted in a very large number of files. For the purity of the experiment, I followed the dataset used in Python for predicting the body of a function. Therefore, I only took files that contain functions. From these, I used the `create_dataset.py` script to create a dataset, which consists of rows in the format:

| Signature                         | Body                                                                                                            | Docstring                                                                                                                                                            | ID   |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| `fun testYield()`                 | `{ val arg: UserKlass = UserKlass() val buildee = build { yield(id(arg)) }`                                     | `// FIR_IDENTICAL // CHECK_TYPE_WITH_EXACT`                                                                                                                          | e673 |
| `fun testMaterialize(),`          | `{ fun consume(arg: UserKlass) {}`                                                                              | `// exact type equality check — turns unexpected compile-time behavior into red code // considered to be non-user-reproducible code for the purposes of these tests` | 2ed8 |
| `fun test(),`                     | `{ val buildee = build { setTypeVariable(TargetType()) extensionSetOutProjectedTypeVariable(DifferentType()) }` | `// ISSUE: KT-57707 // CHECK_TYPE_WITH_EXACT`                                                                                                                        | fe98 |
| `fun setTypeVariable(value: TV),` | `{ storage = value }`                                                                                           | `// exact type equality check — turns unexpected compile-time behavior into red code // considered to be non-user-reproducible code for the purposes of these tests` | 7aec |

## Fine-tuning and Evaluation

For training, I used the [phi-2](https://huggingface.co/microsoft/phi-2) model and trained it on the dataset I created. The training was conducted on [Lightning.AI](https://lightning.ai/). The [notebook](https://github.com/asahium/Improving-LLMs-on-underrepresented-programming-languages/blob/main/fine-tuning.ipynb) with the training code is available. For fine-tuning, I used the following LoRa parameters:

```python
config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules=["dense", "fc2","q_proj","k_proj","v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
```

The results of the predictions on the test sample (notebook with the prediction code [here](https://github.com/asahium/Improving-LLMs-on-underrepresented-programming-languages/blob/main/evaluation.ipynb) and code for computing metrics [here](https://github.com/asahium/Improving-LLMs-on-underrepresented-programming-languages/blob/main/evaluator.py)):

| Prediction File            | Edit Similarity (Edit Sim) | Exact Match (EM) |
| -------------------------- | -------------------------- | ---------------- |
| `kotlin_predictions_0.txt` | 11.17                      | 0.0%             |
| `kotlin_predictions_f.txt` | 15.67                      | 0.0%             |
| `python_predictions_0.txt` | 40.18                      | 6.0%             |
| `python_predictions_f.txt` | 38.26                      | 5.0%             |

We see that after fine-tuning, the quality on the test sample improved. However, the quality on Python has deteriorated. This could be due to the model slightly overfitting on the Kotlin dataset.

Also, if we look at the predictions, it can be noticed that the model predicts practically the same lines of brackets in Kotlin. Actually, I think this is a good sign that the model has started to differentiate Kotlin code from Python. To improve the quality of code generations, one could try increasing the dataset size, enlarging the model size, increasing the number of training epochs, changing fine-tuning parameters, etc.
