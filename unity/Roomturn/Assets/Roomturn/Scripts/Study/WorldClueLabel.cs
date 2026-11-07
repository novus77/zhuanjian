using UnityEngine;

namespace Roomturn
{
    public sealed class WorldClueLabel : MonoBehaviour
    {
        public Material textMaterial;
        public Font font;
        Material material;

        void Awake()
        {
            font.RequestCharactersInTexture("日入门，可归", 48);
            var text = gameObject.AddComponent<TextMesh>();
            text.text = "日入门，可归";
            text.font = font;
            text.fontSize = 48;
            text.characterSize = .022f;
            text.anchor = TextAnchor.MiddleCenter;
            text.color = new Color(.15f, .08f, .035f);
            material = new Material(textMaterial);
            material.mainTexture = font.material.mainTexture;
            GetComponent<MeshRenderer>().sharedMaterial = material;
            Font.textureRebuilt += RefreshTexture;
        }

        void RefreshTexture(Font changed)
        {
            if (changed == font) material.mainTexture = font.material.mainTexture;
        }

        void OnDestroy()
        {
            Font.textureRebuilt -= RefreshTexture;
            if (material != null) Destroy(material);
        }
    }
}
