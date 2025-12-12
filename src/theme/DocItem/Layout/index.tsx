/**
 * Custom DocItem Layout - Adds read time estimate to pages
 */

import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import type LayoutType from '@theme/DocItem/Layout';
import type { WrapperProps } from '@docusaurus/types';
import { ReadTimeEstimate } from '@site/src/components/ProgressIndicator';

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props): JSX.Element {
  return (
    <div>
      <ReadTimeEstimate />
      <Layout {...props} />
    </div>
  );
}
