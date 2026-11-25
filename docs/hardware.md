# Hardware of the three machines (T14)

Used for the local-model decision (T24). Update a row when a machine changes.

| | Omar | Mohamed Samy | Amir |
|---|---|---|---|
| CPU | 10-core, MacBook Air | Intel i7, 11th gen, laptop | Intel i5, 12th gen, laptop |
| GPU | 10-core Apple GPU, integrated | NVIDIA GTX 1650 | NVIDIA RTX 3050 |
| GPU memory | Shared: 24 GB unified | 4 GB dedicated | 6 GB dedicated |
| RAM | 24 GB (same pool as the GPU) | 16 GB | 16 GB |
| Storage | 512 GB SSD | 256 GB SSD + 1 TB HDD | 512 GB |
| OS | macOS 27.0.1 | Windows 11 Pro | Windows 11 |
| Local model now | Qwen 3.5 4B, Gemma 4 12B (not yet measured) | Qwen 3.5, 0.8B | Qwen 3.5, 0.8B |

## Notes

- Omar's Mac has a fanless design, so long runs may slow down.
- Mohamed Samy keeps model files on the SSD, not the HDD.