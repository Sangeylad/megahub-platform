<?php

namespace OtomaticAi\Utils;

use Exception;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Image
{
    private $content;
    private $mimeType;
    private $attachmentId;

    public function __construct($content, $mimeType = "image/jpeg")
    {
        $this->content = $content;
        $this->mimeType = $mimeType;
    }

    public function save($name, $description = null, $legend = null)
    {
        if ($this->attachmentId === null) {
            $extension = $this->mimeTypeToExtension($this->mimeType);

            // store media
            $uploadBits = wp_upload_bits($name . '.' . $extension, null, $this->content);

            if (!$uploadBits['error']) {
                $wpFileType = wp_check_filetype($uploadBits["file"], null);

                $attachment = [
                    'guid'           => $uploadBits["file"],
                    'post_mime_type' => $wpFileType['type'],
                    'post_title'     => $name,
                    'post_content'   => '',
                    'post_status'    => 'inherit',
                ];
                if (!empty($legend)) {
                    $attachment["post_excerpt"] = $legend;
                }
                $attachmentId = wp_insert_attachment($attachment, $uploadBits["file"]);

                if (!is_wp_error($attachmentId)) {

                    // fire wp_handle_upload filter
                    apply_filters('wp_handle_upload', [
                        'file' => $uploadBits["file"],
                        'url'  => $uploadBits["url"],
                        'type' => $wpFileType['type']
                    ]);
                    require_once ABSPATH . 'wp-admin/includes/image.php';

                    // generate attachement metadata
                    $attachmentMetadata = wp_generate_attachment_metadata($attachmentId, $uploadBits["file"]);
                    wp_update_attachment_metadata($attachmentId, $attachmentMetadata);

                    if (!empty($description)) {
                        update_post_meta($attachmentId, '_wp_attachment_image_alt', $description);
                    }
                    $this->attachmentId = $attachmentId;
                }
            }
        }

        return $this->attachmentId;
    }

    static public function fromUrl($url)
    {
        $mediaFile = wp_remote_get($url);
        if (is_wp_error($mediaFile)) {
            throw new Exception("Can not download image url `" . $url . "`. Error: " . $mediaFile->get_error_message());
        }
        return new self($mediaFile["body"], Arr::get($mediaFile, 'headers.content-type', 'image/jpeg'));
    }

    static public function fromPath($path)
    {
        $mediaFile = file_get_contents($path);
        if ($mediaFile === false) {
            throw new Exception("Can not load image path `" . $path . "`.");
        }
        $f = finfo_open();
        return new self($mediaFile, finfo_buffer($f, $mediaFile, FILEINFO_MIME_TYPE));
    }

    static public function fromBase64($base64)
    {
        $content = base64_decode($base64);
        $f = finfo_open();
        return new self($content, finfo_buffer($f, $content, FILEINFO_MIME_TYPE));
    }

    static private function mimeTypeToExtension($mime)
    {
        $mimeTypes = [
            'image/png' => 'png',
            'image/jpeg' => 'jpg',
            'image/gif' => 'gif',
            'image/bmp' => 'bmp',
            'image/vnd.microsoft.icon' => 'ico',
            'image/tiff' => 'tif',
            'image/svg+xml' => 'svg',
            'image/webp' => 'webp',
        ];
        $extension = str_replace(
            array_keys($mimeTypes),
            array_values($mimeTypes),
            $mime,
            $count
        );
        // set default fileExtension if not found
        if ((int) $count == 0) {
            $extension = 'jpg';
        }

        return $extension;
    }
}
