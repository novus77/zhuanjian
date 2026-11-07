using System.IO;
using UnityEditor;
using UnityEngine;

namespace Roomturn.Editor
{
    public static class Lux3DMaterial
    {
        public static Material Load(string materialPath, string baseColorPath)
        {
            var material = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (material == null)
            {
                material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(material, materialPath);
            }
            var sourcePath = baseColorPath.Replace("_BaseColor.png", "_MetallicRoughness.png");
            var packedPath = baseColorPath.Replace("_BaseColor.png", "_MetallicSmoothness.png");
            // glTF stores roughness in G and metalness in B. URP expects metalness
            // in R and smoothness (1 - roughness) in A, both as linear data.
            var source = new Texture2D(2, 2, TextureFormat.RGBA32, false, true);
            if (!source.LoadImage(File.ReadAllBytes(sourcePath)))
                throw new System.InvalidOperationException("Cannot load PBR texture: " + sourcePath);
            var pixels = source.GetPixels32();
            for (var index = 0; index < pixels.Length; index++)
                pixels[index] = new Color32(pixels[index].b, 0, 0, (byte)(255 - pixels[index].g));
            var packed = new Texture2D(source.width, source.height, TextureFormat.RGBA32, false, true);
            packed.SetPixels32(pixels);
            packed.Apply();
            File.WriteAllBytes(packedPath, packed.EncodeToPNG());
            Object.DestroyImmediate(source);
            Object.DestroyImmediate(packed);
            AssetDatabase.ImportAsset(packedPath, ImportAssetOptions.ForceSynchronousImport);
            var importer = (TextureImporter)AssetImporter.GetAtPath(packedPath);
            importer.sRGBTexture = false;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = false;
            importer.SaveAndReimport();
            material.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(baseColorPath));
            material.SetTexture("_MainTex", AssetDatabase.LoadAssetAtPath<Texture2D>(baseColorPath));
            material.SetTexture("_MetallicGlossMap", AssetDatabase.LoadAssetAtPath<Texture2D>(packedPath));
            material.EnableKeyword("_METALLICSPECGLOSSMAP");
            material.SetColor("_BaseColor", Color.white);
            material.SetFloat("_Metallic", 1f);
            material.SetFloat("_Smoothness", 1f);
            material.SetFloat("_SmoothnessTextureChannel", 0f);
            EditorUtility.SetDirty(material);
            return material;
        }
    }
}
