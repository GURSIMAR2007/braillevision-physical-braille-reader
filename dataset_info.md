# Dataset Information

This submission folder contains a small bundled sample set for local testing.

## Bundled Sample Inputs

- `sample_inputs/physical_front_view_1.jpeg`
  Real front-view embossed Braille image provided by the team.

- `sample_inputs/physical_front_view_line_crop.jpeg`
  Tighter crop of the same physical Braille sample, used to make testing easier.

- `sample_inputs/udhr_braille.jpg`
  Braille reference image used as an extra test/reference sample.

## Source Notes

- The physical Braille image was provided by the team.
- The cropped line image was created from the team sample for easier debugging.
- The UDHR Braille image is included as a reference-style sample image.

## Current Use

These images are used for local inference testing only in this baseline folder.

## Future Improvement

For a stronger submission, the team should add:

- more real physical Braille photos
- known correct text labels
- train/validation/test split
- annotation files if a detector model is trained
