# Diagnostics

## Determine mip-chain completeness

Read `width`, `height`, `depth`, and `mipLevels` from `texdiag info`.
The maximum mip count is:

```text
floor(log2(max(width, height, depth))) + 1
```

This formula applies to power-of-two and non-power-of-two dimensions.
For arrays and cubemaps, `mipLevels` gives the count for each item or face.

- `mipLevels == maximum`: The chain reaches 1×1 or 1×1×1.
- `mipLevels < maximum`: The chain stops before the smallest level.
- `mipLevels == 1`: The DDS stores only the top level.

These results describe the stored subresources. DDS does not record why a chain stops early.

## Quantify stored image data

`width`, `height`, and `depth` describe the top level.
`pixel size` is the total DirectXTex pixel-buffer size for all stored subresources.
It is not the DDS file size.

DDS metadata does not contain an intended resolution or size budget.

## Determine decoded alpha variation

Read the fourth component of each `Minimum`, `Average`, and `Maximum` tuple from `texdiag analyze`.
The component applies to the reported item and mip.

- Equal minimum and maximum values indicate constant alpha at the displayed precision.
- Different minimum and maximum values indicate varying alpha.
- For UNORM formats, `1` is the maximum representable alpha value.
- For UNORM formats, `0` is the minimum representable alpha value.

Stored `alpha mode` does not determine whether decoded alpha is constant or varying.
DDS does not record the Skyrim-specific purpose of the alpha channel.

## Compare DDS files for the same game path

Run `info` and `analyze` for each physical DDS file.
Compare these reported properties:

- Dimensions
- Mip count
- Array size and topology
- Format and `_SRGB` suffix
- Stored alpha mode
- Decoded channel ranges
- `pixel size`.

PNG previews show the decoded top mip as 8-bit display data.
For cubemaps and arrays, a PNG preview shows only the first face or item.
